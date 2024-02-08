from datetime import datetime
from typing import List, Dict, Set, Tuple

import geopy.distance
import numpy as np
from apache_beam import DoFn
from apache_beam.transforms.window import TimestampedValue

from dataflow.bay_area_511_event_pb2 import Event
from dataflow.pems_pb2 import PeMS
from dataflow.segment_definition import SegmentDefinition
from dataflow.weather_pb2 import Weather


class WeatherTransformDoFn(DoFn):
    __city_to_segments: Dict[str, Set[int]] = dict()

    def __init__(self, segments: List[SegmentDefinition]):
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

    def __init__(self, segments: List[SegmentDefinition]):
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

    def __init__(self, segments: List[SegmentDefinition]):
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
    __segments: List[SegmentDefinition] = []

    def __init__(self, segments: List[SegmentDefinition]):
        super().__init__()
        self.__segments = segments

    def process(self, element):
        segment_id, data = element
        t = self.__get_latest_t(element['bay_area_511_event'] + element['pems'] + element['weather'])
        features = self.get_event_features(element['bay_area_511_event'], segment_id, t)

    def get_event_features(self, events: List[Event], segment_id: int, t: int) -> List[float]:
        EVENT_TYPE_TO_IDX = ["CONSTRUCTION", "SPECIAL_EVENT", "INCIDENT", "WEATHER_CONDITION", "ROAD_CONDITION", "None"]
        score = 0.0
        event_type = EVENT_TYPE_TO_IDX[-1]
        for event in events:
            new_score = self.__get_event_score(event, segment_id, t)
            if new_score > score:
                score = new_score
                event_type = event.event_type
        event_type_ohe = [0.0] * len(EVENT_TYPE_TO_IDX)
        event_type_ohe[EVENT_TYPE_TO_IDX.index(event_type)] = 1.0
        return event_type_ohe + [score]

    def __get_event_score(self, event: Event, segment_id: int, t: int) -> float:
        SEVERITY_TO_SCORE = {"MINOR": 1, "MODERATE": 2, "MAJOR": 3, "SEVERE": 4, "UNKNOWN": 1}
        return (SEVERITY_TO_SCORE[event.severity] *
                (np.exp(-float(t - event[3]) / 1800)
                 + np.exp(-geopy.distance.geodesic(reversed(event.geography_point.coordinates),
                                                   self.__get_segment(segment_id)['representative_point']).miles / 5)))

    def __get_segment(self, idx: int) -> SegmentDefinition:
        return next(segment for segment in self.__segments if segment['id'] == idx)

    def __get_latest_t(self, rows: List[TimestampedValue]):
        return max([row.timestamp for row in rows])
