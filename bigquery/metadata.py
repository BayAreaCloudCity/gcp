from typing import TypedDict, Tuple, Dict, List
from google.cloud import bigquery
import os

class Segment(TypedDict):
    id: int
    city: str
    representative_point: Tuple[float, float]
    station_ids: Dict[str, float]  # TODO: Why str?


def get_metadata(version: int) -> List[Segment]:
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