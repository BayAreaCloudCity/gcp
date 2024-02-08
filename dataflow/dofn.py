from datetime import datetime
from typing import List, Dict, Set, Tuple
from zoneinfo import ZoneInfo

import geopy.distance
import numpy as np
from apache_beam import DoFn
from apache_beam.runners.common import Timestamp
from apache_beam.transforms.window import TimestampedValue

from pubsub.bay_area_511_event_pb2 import Event
from pubsub.pems_pb2 import PeMS
from pubsub.processed_pb2 import Processed
from bigquery.metadata import Segment
from pubsub.weather_pb2 import Weather


class WeatherTransformDoFn(DoFn):
    __city_to_segments: Dict[str, Set[int]] = dict()

    def __init__(self, segments: List[Segment]):
        super().__init__()
        for segment in segments:
            if segment['city'] not in self.__city_to_segments:
                self.__city_to_segments[segment['city']] = set()
            self.__city_to_segments.get(segment['city']).add(segment['id'])

    def process(self, row, *args, **kwargs):
        weather = Weather()
        weather.ParseFromString(row)
        ts = weather.dt
        for id in self.__city_to_segments.get(weather.name, set()):
            yield id, TimestampedValue(weather, ts)


class BayArea511EventTransformDoFn(DoFn):
    __segment_to_coord: Dict[int, Tuple[float, float]] = dict()
    MAXIMUM_DISTANCE_MILES = 10

    def __init__(self, segments: List[Segment]):
        super().__init__()
        for segment in segments:
            self.__segment_to_coord[segment['id']] = segment['representative_point']

    def process(self, row, *args, **kwargs):
        event = Event()
        event.ParseFromString(row)
        ts = datetime.fromisoformat(event.created).timestamp()
        for id, coord in self.__segment_to_coord.items():
            distance = geopy.distance.geodesic(reversed(event.geography_point.coordinates),
                                               coord).miles  # PeMS coord are in [lat, lon] but we require [lon, lat]
            if distance <= self.MAXIMUM_DISTANCE_MILES:
                yield id, TimestampedValue(event, ts)


class PeMSTransformDoFn(DoFn):
    __station_to_segment: Dict[int, Set[int]] = dict()

    def __init__(self, segments: List[Segment]):
        super().__init__()
        for segment in segments:
            for station_id in segment['station_ids']:
                if int(station_id) not in self.__station_to_segment:
                    self.__station_to_segment[int(station_id)] = set()
                self.__station_to_segment.get(int(station_id)).add(segment['id'])

    def process(self, row, *args, **kwargs):
        pems = PeMS()
        pems.ParseFromString(row)
        ts = datetime.strptime(pems.time, "%m/%d/%Y %H:%M:%S").timestamp()
        for id in self.__station_to_segment.get(pems.station_id, set()):
            yield id, TimestampedValue(pems, ts)


class SegmentFeatureTransformDoFn(DoFn):
    __segments: List[Segment] = []

    def __init__(self, segments: List[Segment]):
        super().__init__()
        self.__segments = segments

    def process(self, element):
        segment_id, data = element
        t = self.__get_latest_t(data['bay_area_511_event'] + data['pems'] + data['weather'])
        features = self.get_event_features(data['bay_area_511_event'], segment_id, t) + \
                   self.get_pems_feature(data['pems'], segment_id) + \
                   self.get_weather_features(data['weather']) + \
                   self.get_time_features(t)
        processed = Processed(coefficients=features, model_version=1, event_timestamp=t.seconds(),
                              segment_id=segment_id)
        yield processed

    def get_event_features(self, events: List[TimestampedValue[Event]], segment_id: int, t: Timestamp) -> List[float]:
        EVENT_TYPE_TO_IDX = ["CONSTRUCTION", "SPECIAL_EVENT", "INCIDENT", "WEATHER_CONDITION", "ROAD_CONDITION", "None"]
        score = 0.0
        event_type = EVENT_TYPE_TO_IDX[-1]
        for event in events:
            new_score = self.__get_event_score(event, segment_id, t)
            if new_score > score:
                score = new_score
                event_type = event.value.event_type
        event_type_ohe = [0.0] * len(EVENT_TYPE_TO_IDX)
        event_type_ohe[EVENT_TYPE_TO_IDX.index(event_type)] = 1.0
        return event_type_ohe + [score]

    def get_weather_features(self, weather: List[TimestampedValue[Weather]]) -> List[float]:
        WEATHER_CONDITIONS = ["Thunderstorm", "Drizzle", "Rain", "Snow", "Mist", "Smoke", "Haze", "Dust", "Fog", "Sand",
                              "Ash", "Squall", "Tornado", "Clear", "Clouds"]
        weather_encoding = [0.0] * len(WEATHER_CONDITIONS)

        most_recent = max(weather, key=lambda x: x.timestamp, default=None)
        if most_recent is not None:
            weather_encoding[WEATHER_CONDITIONS.index(most_recent.value.weather[0].main)] = 1.0
            weather_encoding += [most_recent.value.visibility]
        else:
            weather_encoding += 0.0  # TODO: Impute better
        return weather_encoding

    def get_pems_feature(self, pems: List[TimestampedValue[PeMS]], segment_id: int):
        return [0.0]  # TODO

    def get_time_features(self, t: Timestamp):
        DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        HOURS_OF_DAY = [f"Hour{i}" for i in range(24)]
        days_ohe = [0.0] * len(DAYS_OF_WEEK)
        hours_ohe = [0.0] * len(HOURS_OF_DAY)
        dt = datetime.fromtimestamp(t.seconds(), tz=ZoneInfo("America/Los_Angeles"))
        days_ohe[dt.weekday()] = 1.0
        hours_ohe[dt.hour] = 1.0
        return days_ohe + hours_ohe

    def __get_event_score(self, event: TimestampedValue[Event], segment_id: int, t: Timestamp) -> float:
        SEVERITY_TO_SCORE = {"Minor": 1, "Moderate": 2, "Major": 3, "Severe": 4, "Unknown": 1}
        return (SEVERITY_TO_SCORE[event.value.severity] *
                (np.exp(-float(t.seconds() - event.timestamp.seconds()) / 1800)
                 + np.exp(-geopy.distance.geodesic(reversed(event.value.geography_point.coordinates),
                                                   self.__get_segment(segment_id)['representative_point']).miles / 5)))

    def __get_segment(self, idx: int) -> Segment:
        return next(segment for segment in self.__segments if segment['id'] == idx)

    def __get_latest_t(self, rows: List[TimestampedValue]):
        return max([row.timestamp for row in rows])
