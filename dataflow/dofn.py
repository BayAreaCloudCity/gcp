from datetime import datetime
from typing import List, Dict, Set, Tuple
from zoneinfo import ZoneInfo

import geopy.distance
import numpy as np
from apache_beam import DoFn
from apache_beam.runners.common import Timestamp
from apache_beam.transforms.window import TimestampedValue

from bigquery.metadata import Segment

# ============ Timestamp Extraction ============


def get_weather_timestamp(row) -> int:
    """Extract timestamp for a weather record, in unix timestamp (seconds)."""
    return row['dt']


def get_bay_area_511_event_timestamp(row) -> int:
    """Extract timestamp for a 511.org record, in unix timestamp (seconds)."""
    return int(datetime.fromisoformat(row['created']).timestamp())


def get_pems_timestamp(row) -> int:
    """
    Extract timestamp for a PeMS record, in unix timestamp (seconds).
    PeMS data need to be converted back to UTC time as they're based on Pacific Time.
    """
    return int(datetime.strptime(row['time'], "%m/%d/%Y %H:%M:%S")
               .replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp())

# ============ Segment Mapping ============


class WeatherTransformDoFn(DoFn):
    """
    Transform a weather record to a timestamped record, whose key is the segment id and value is the weather data.
    The timestamp is based on the event time, which in this case would be the time when weather info was last updated.
    A weather record could be transformed into multiple timestamped records, if a city has multiple segments in it.
    """
    __city_to_segments: Dict[str, Set[int]] = dict()

    def __init__(self, segments: List[Segment]):
        for segment in segments:
            # Create a map between each city and its segments using the metadata.
            if segment['city'] not in self.__city_to_segments:
                self.__city_to_segments[segment['city']] = set()
            self.__city_to_segments.get(segment['city']).add(segment['id'])

    def process(self, row, *args, **kwargs):
        ts = get_weather_timestamp(row)
        # Find the corresponding segment IDs and send the values.
        for id in self.__city_to_segments.get(row['name'], set()):
            yield TimestampedValue((id, row), ts)


class BayArea511EventTransformDoFn(DoFn):
    """
    Transform a weather record to a timestamped record, whose key is the segment id and value is the weather data.
    A weather record could be transformed into multiple timestamped records, if a city has multiple segments in it.
    """
    __segment_to_coord: Dict[int, Tuple[float, float]] = dict()
    MAXIMUM_DISTANCE_MILES = 10

    def __init__(self, segments: List[Segment]):
        for segment in segments:
            self.__segment_to_coord[segment['id']] = segment['representative_point']

    def process(self, row, *args, **kwargs):
        ts = get_bay_area_511_event_timestamp(row)
        for id, coord in self.__segment_to_coord.items():
            distance = geopy.distance.geodesic(reversed(row['geography_point']['coordinates']),
                                               coord).miles  # PeMS coord are in [lat, lon] but we require [lon, lat]
            if distance <= self.MAXIMUM_DISTANCE_MILES:
                yield TimestampedValue((id, row), ts)


class PeMSTransformDoFn(DoFn):
    __station_to_segment: Dict[int, Set[int]] = dict()

    def __init__(self, segments: List[Segment]):
        for segment in segments:
            for station_id in segment['station_ids']:
                if int(station_id) not in self.__station_to_segment:
                    self.__station_to_segment[int(station_id)] = set()
                self.__station_to_segment.get(int(station_id)).add(segment['id'])

    def process(self, row, *args, **kwargs):
        ts = get_pems_timestamp(row)
        for id in self.__station_to_segment.get(row['station_id'], set()):
            yield TimestampedValue((id, row), ts)


class SegmentFeatureTransformDoFn(DoFn):
    __segments: List[Segment] = []
    __metadata_version: int

    def __init__(self, segments: List[Segment], metadata_version: int):
        self.__segments = segments
        self.__metadata_version = metadata_version

    def process(self, element, window=DoFn.WindowParam):
        segment_id, data = element
        t = window.end
        features = self.get_event_features(data['bay_area_511_event'], segment_id, t) + \
                   self.get_pems_feature(data['pems'], segment_id) + \
                   self.get_weather_features(data['weather']) + \
                   self.get_time_features(t)
        yield {
            "coefficients": features,
            "metadata_version": self.__metadata_version,
            "timestamp": t.seconds(),
            "segment_id": segment_id,
            "publish_time": t.micros # in streaming mode, this will be overwritten with actual pubsub time
        }

    def get_event_features(self, events: List[dict], segment_id: int, t: Timestamp) -> List[float]:
        EVENT_TYPE_TO_IDX = ["CONSTRUCTION", "SPECIAL_EVENT", "INCIDENT", "WEATHER_CONDITION", "ROAD_CONDITION", "None"]
        score = 0.0
        event_type = EVENT_TYPE_TO_IDX[-1]
        for event in events:
            new_score = self.__get_event_score(event, segment_id, t)
            if new_score > score:
                score = new_score
                event_type = event['event_type']
        event_type_ohe = [0.0] * len(EVENT_TYPE_TO_IDX)
        event_type_ohe[EVENT_TYPE_TO_IDX.index(event_type)] = 1.0
        return event_type_ohe + [score]

    def get_weather_features(self, weather: List[dict]) -> List[float]:
        WEATHER_CONDITIONS = ["Thunderstorm", "Drizzle", "Rain", "Snow", "Mist", "Smoke", "Haze", "Dust", "Fog", "Sand",
                              "Ash", "Squall", "Tornado", "Clear", "Clouds"]
        weather_encoding = [0.0] * len(WEATHER_CONDITIONS)

        most_recent = max(weather, key=lambda x: x['dt'], default=None)

        if most_recent is not None:
            weather_encoding[WEATHER_CONDITIONS.index(most_recent['weather'][0]['main'])] = 1.0
            weather_encoding += [most_recent['visibility']]
        else:
            weather_encoding[WEATHER_CONDITIONS.index("Clouds")] = 1.0
            weather_encoding += [10000.0]  # TODO: Impute better
        return weather_encoding

    def get_pems_feature(self, pems: List[dict], segment_id: int) -> List[float]:
        segment = self.__get_segment(segment_id)
        distance = segment["end_postmile"] - segment["start_postmile"]
        l = 0.0
        for id, weight in segment['station_ids'].items():
            stations = list(filter(lambda x: x['station_id'] == int(id), pems))
            most_recent = max(stations, key=get_pems_timestamp, default=None)
            if most_recent is not None:
                l += weight / most_recent['average_speed']
            else:
                l += weight / 60.0 # TODO: Impute Better
        return [distance / l]


    def get_time_features(self, t: Timestamp):
        DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        HOURS_OF_DAY = [f"Hour{i}" for i in range(24)]
        days_ohe = [0.0] * len(DAYS_OF_WEEK)
        hours_ohe = [0.0] * len(HOURS_OF_DAY)
        dt = datetime.fromtimestamp(t.seconds(), tz=ZoneInfo("America/Los_Angeles"))
        days_ohe[dt.weekday()] = 1.0
        hours_ohe[dt.hour] = 1.0
        return days_ohe + hours_ohe

    def __get_event_score(self, event: dict, segment_id: int, t: Timestamp) -> float:
        SEVERITY_TO_SCORE = {"Minor": 1, "Moderate": 2, "Major": 3, "Severe": 4, "Unknown": 1}
        return (SEVERITY_TO_SCORE[event['severity']] *
                (np.exp(-float(t.seconds() - get_bay_area_511_event_timestamp(event)) / 1800)
                 + np.exp(-geopy.distance.geodesic(reversed(event['geography_point']['coordinates']),
                                                   self.__get_segment(segment_id)['representative_point']).miles / 5)))

    def __get_segment(self, idx: int) -> Segment:
        return next(segment for segment in self.__segments if segment['id'] == idx)
