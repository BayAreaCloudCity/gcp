import os
from typing import TypedDict, Tuple, Dict, List, Optional

from google.cloud import bigquery


class Segment(TypedDict):
    """Segment definition"""
    id: int
    city: str  # city which the segment is in
    start_postmile: float  # postmile of the points below
    end_postmile: float
    representative_postmile: float  #
    start_point: Tuple[float, float]  # coordinate of the starting point
    end_point: Tuple[float, float]  # coordinate of the end point
    representative_point: Tuple[float, float]  # coordinate of the point to represent the segment
    station_ids: Dict[str, float]  # PeMS station weights


class Metadata(TypedDict):
    segments: List[Segment]  # segment definition
    model: List[float]  # coefficients for model


METADATA_CACHE: Optional[int] = None
METADATA_VERSION_CACHE: Optional[Metadata] = None


def get_metadata(version: int) -> Metadata:
    """Get model metadata"""
    global METADATA_CACHE, METADATA_VERSION_CACHE

    if METADATA_VERSION_CACHE == version:
        return METADATA_CACHE

    client = bigquery.Client(project=os.environ['PROJECT_ID'])
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("version", "INT64", version)
        ],
    )

    query_job = client.query(
        f"""
            SELECT *
            FROM `{os.environ['METADATA_DATASET_ID']}.{os.environ['METADATA_TABLE_ID']}`
            WHERE version = @version
            """, job_config=job_config)

    result = query_job.result(max_results=1)
    metadata = next(result).data

    # cache the metadata in memory in case the current Cloud Function instance will be reused.
    METADATA_CACHE = metadata
    METADATA_VERSION_CACHE = version

    return metadata


def get_schema(dataset: str, table: str):
    """Get the schema of a BigQuery table"""
    client = bigquery.Client(project=os.environ['PROJECT_ID'])
    return client.get_table(f"{dataset}.{table}").schema
