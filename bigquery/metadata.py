from typing import TypedDict, Tuple, Dict, List
from google.cloud import bigquery
import os


class Segment(TypedDict):
    id: int
    city: str
    start_postmile: float
    end_postmile: float
    representative_point: Tuple[float, float]
    station_ids: Dict[str, float]  # TODO: Why str?


class Metadata(TypedDict):
    segments: List[Segment]
    model: List[float]


def get_metadata(version: int) -> Metadata:
    client = bigquery.Client(project=os.environ['PROJECT_ID'])
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("version", "INT64", version)
        ],
    )

    query_job = client.query(
        f"""
            SELECT *
            FROM `cloud_city.metadata`
            WHERE version = @version
            """, job_config=job_config)

    result = query_job.result(max_results=1)
    return next(result).data


def get_schema(dataset: str, table: str):
    client = bigquery.Client(project=os.environ['PROJECT_ID'])
    return client.get_table(f"{dataset}.{table}").schema
