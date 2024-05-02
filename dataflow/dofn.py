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


def get_publish_timestamp(row) -> int:
    """
    Extract (publish) timestamp for any PubSub entries in BigQuery, in unix timestamp (seconds).
    """
    return int(row['publish_time'] / 1e6)


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
            # Create a map between each segment IDs and their coordinates.
            self.__segment_to_coord[segment['id']] = segment['representative_point']

    def process(self, row, *args, **kwargs):
        ts = get_bay_area_511_event_timestamp(row)
        for id, coord in self.__segment_to_coord.items():
            # Yield an event to a segment if it's within the range.
            distance = geopy.distance.geodesic(reversed(row['geography_point']['coordinates']),
                                               coord).miles  # PeMS coord are in [lat, lon] but we require [lon, lat]
            if distance <= self.MAXIMUM_DISTANCE_MILES:
                yield TimestampedValue((id, row), ts)


class PeMSTransformDoFn(DoFn):
    __station_to_segment: Dict[int, Set[int]] = dict()

    def __init__(self, segments: List[Segment]):
        for segment in segments:
            for station_id in segment['station_ids']:
                # Create a map between each station and their segments.
                if int(station_id) not in self.__station_to_segment:
                    # A PeMS station can be mapped to multiple segments.
                    self.__station_to_segment[int(station_id)] = set()
                self.__station_to_segment.get(int(station_id)).add(segment['id'])

    def process(self, row, *args, **kwargs):
        ts = get_pems_timestamp(row)
        # Map each station to 0 or more segments
        for id in self.__station_to_segment.get(row['station_id'], set()):
            yield TimestampedValue((id, row), ts)


# ============ Feature Tranformation ============


class SegmentFeatureTransformDoFn(DoFn):
    """
    Per-segment transformation into final processed features, after grouping.
    See design doc for mathmatical representation of the transformation below.
    """
    __segments: List[Segment] = []  # segment definition
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
            "publish_time": t.micros  # in streaming mode, this will be overwritten with actual pubsub time
        }

    def get_event_features(self, events: List[dict], segment_id: int, t: Timestamp) -> List[float]:
        """
        Transform event features.
        Results will be [...OHE of event type..., severity score] of the most severe event.
        """
        possible_event_types = ["CONSTRUCTION", "SPECIAL_EVENT", "INCIDENT",
                                "WEATHER_CONDITION", "ROAD_CONDITION", "None"]
        score = 0.0  # default score is 0, indicating no events
        event_type = possible_event_types[-1]  # default event type is None
        for event in events:
            new_score = self.__get_event_score(event, segment_id, t)
            # get the most severe event
            if new_score > score:
                score = new_score
                event_type = event['event_type']
        event_type_ohe = self.__ohe(possible_event_types, event_type)  # set event type
        return event_type_ohe + [score]

    def get_weather_features(self, weather: List[dict]) -> List[float]:
        """
        Transform weather features.
        Results will be [...OHE of weather conditions..., visibility] of the most recent data.
        """
        possible_weather_conditions = ["Thunderstorm", "Drizzle", "Rain", "Snow", "Mist", "Smoke", "Haze", "Dust",
                                       "Fog", "Sand", "Ash", "Squall", "Tornado", "Clear", "Clouds"]

        most_recent = max(weather, key=get_weather_timestamp, default=None)  # we only consider the most recent one
        if most_recent is not None:
            weather_encoding = self.__ohe(possible_weather_conditions, most_recent['weather'][0]['main'])
            weather_encoding += [most_recent['visibility']]
        else:  # No data is available, impute it by assuming clear weather.
            weather_encoding = self.__ohe(possible_weather_conditions, "Clear")
            weather_encoding += [10000.0]
        return weather_encoding

    def get_pems_feature(self, pems: List[dict], segment_id: int) -> List[float]:
        """
        Transform PeMS features.
        Results will be [speed], using the most recent data of the stations required.
        """
        segment = self.__get_segment(segment_id)
        distance = segment["end_postmile"] - segment["start_postmile"]  # segment distance
        l = 0.0
        for id, weight in segment['station_ids'].items():
            stations = list(filter(lambda x: x['station_id'] == int(id), pems))
            most_recent = max(stations, key=get_pems_timestamp, default=None)  # most recent data
            if most_recent is not None:
                l += weight / most_recent['average_speed']
            else:  # if data is missing, imputing it with 60mph.
                l += weight / 60.0
        return [distance / l]

    def get_time_features(self, t: Timestamp):
        """
        Transform time features.
        Results will be [...OHE of day of the week..., OHE of hour of the day]
        """
        dt = datetime.fromtimestamp(t.seconds(), tz=ZoneInfo("America/Los_Angeles"))
        return self.__ohe(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], dt.weekday()) + self.__ohe(
            [f"Hour{i}" for i in range(24)], dt.hour)

    def __get_event_score(self, event: dict, segment_id: int, t: Timestamp) -> float:
        """
        Generate event severity score for an event. See explanation in model design doc.
        """
        SEVERITY_TO_SCORE = {"Minor": 1, "Moderate": 2, "Major": 3, "Severe": 4, "Unknown": 1}
        return (SEVERITY_TO_SCORE[event['severity']] *
                (np.exp(-float(t.seconds() - get_bay_area_511_event_timestamp(event)) / 1800)
                 + np.exp(-geopy.distance.geodesic(
                            # 511.org coordinates are in reversed order
                            reversed(event['geography_point']['coordinates']),
                            self.__get_segment(segment_id)['representative_point']).miles / 5)))

    def __get_segment(self, idx: int) -> Segment:
        return next(segment for segment in self.__segments if segment['id'] == idx)

    def __ohe(self, choices: List, select: str | int) -> List[float]:
        """
        OHE based on a list.
        """
        encoding = [0.0] * len(choices)
        if isinstance(select, int):
            encoding[select] = 1.0
        else:
            encoding[choices.index(select)] = 1.0
        return encoding
