import csv
import gc
import gzip
import os
from datetime import datetime, timedelta
from io import StringIO
from typing import List
from zoneinfo import ZoneInfo

import requests
import tqdm
from cloudevents.http import CloudEvent
from google.cloud import bigquery
from google.protobuf import json_format

from bigquery.metadata import get_schema
from pubsub.pems_pb2 import PeMS

BASE_URL = "https://pems.dot.ca.gov"


def collect_pems(days_to_fetch: List = None):
    if days_to_fetch is None or len(days_to_fetch) == 0:
        days_to_fetch = [(datetime.now(ZoneInfo("America/Los_Angeles")) - timedelta(days=1)).strftime('%Y_%m_%d')]

    print(f"Download {days_to_fetch} from PeMS.")
    if len(list(filter(lambda x: not x.startswith(days_to_fetch[0][:4]), days_to_fetch))) != 0:
        raise Exception("days_to_fetch does not stay within the same year")

    session = requests.Session()
    # Log in to PeMS
    session.post(
        BASE_URL,
        data={
            "username": os.environ['USERNAME'],
            "password": os.environ['PASSWORD'],
            "login": "Login",
        },
    )

    # get information about available data within a year
    months = session.get(BASE_URL, params={"srq": "clearinghouse",
                                           "district_id": os.environ['DISTRICT_ID'],
                                           "yy": days_to_fetch[0][:4],
                                           "type": "station_5min",
                                           "returnformat": "text"})
    months.raise_for_status()

    for files in months.json()['data'].values():
        for file in files:
            # if any file matches the date we want, download it
            if any(day in file['file_name'] for day in days_to_fetch):
                print(f"Upload {file['file_name']}.")
                gzipped_data = session.get(BASE_URL + file['url'])
                gzipped_data.raise_for_status()
                data = gzip.decompress(gzipped_data.content)

                del gzipped_data
                gc.collect()  # prevent OOM in Cloud Function

                upload(data)


def parse_int(val: str):
    return int(val) if len(val) > 0 else None


def parse_float(val: str):
    return float(val) if len(val) > 0 else None


def upload(pems_data: bytes):
    client = bigquery.Client(project=os.environ['PROJECT_ID'])
    job_config = bigquery.LoadJobConfig(schema=get_schema(os.environ['DATASET_ID'], os.environ['TABLE_ID']))
    data = []

    reader = csv.reader(StringIO(pems_data.decode()), delimiter=",")
    for row in tqdm.tqdm(reader):
        # read through CSV and transform it into protobuf
        pems = PeMS(
            time=row[0],
            station_id=parse_int(row[1]),
            district=parse_int(row[2]),
            freeway=parse_int(row[3]),
            direction=row[4],
            lane_type=row[5],
            station_length=parse_float(row[6]) if len(row[6]) > 0 else 0.0,
            samples=parse_int(row[7]),
            percentage_observed=parse_int(row[8]),
            total_flow=parse_int(row[9]),
            average_occupancy=parse_float(row[10]),
            average_speed=parse_float(row[11]),
            lanes=[]
        )
        offset = 12
        for i in range(0, int((len(row) - offset) / 5)):
            if row[offset + i * 5 + 0] == '' and parse_int(row[offset + i * 5 + 4]) == 0:
                continue  # empty record

            pems.lanes.append(
                PeMS.Lane(
                    samples=parse_int(row[offset + i * 5 + 0]),
                    flow=parse_int(row[offset + i * 5 + 1]),
                    average_occupancy=parse_float(row[offset + i * 5 + 2]),
                    average_speed=parse_float(row[offset + i * 5 + 3]),
                    observed=parse_int(row[offset + i * 5 + 4]) == 1
                ))

        result = json_format.MessageToDict(pems, preserving_proto_field_name=True)
        result['publish_time'] = int(datetime.strptime(pems.time, "%m/%d/%Y %H:%M:%S").replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp() * 1000000)
        data.append(result)
        del pems

    result = client.load_table_from_json(
        data,
        f"{os.environ['DATASET_ID']}.{os.environ['TABLE_ID']}", job_config=job_config).result()
    print(f"{result.output_rows} rows uploaded.")
