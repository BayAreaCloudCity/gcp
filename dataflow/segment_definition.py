from typing import TypedDict, Tuple, Dict


class SegmentDefinition(TypedDict):
    id: int
    city: str
    representative_point: Tuple[float, float]
    station_ids: Dict[str, float]  # TODO: Why str?


