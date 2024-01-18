import gzip
import os
from zoneinfo import ZoneInfo
import requests
import csv
from datetime import datetime, timedelta
import json
from cloudevents.http import CloudEvent
from google.cloud import bigquery
from google.protobuf import json_format
from pems_pb2 import PeMS
import tqdm

BASE_URL = "https://pems.dot.ca.gov"

'''
Environment Variables:
USERNAME: Username for pems.dot.ca.gov
PASSWORD: Password for pems.dot.ca.gov
PROJECT_ID: Current project ID
DATASET_ID: Dataset ID to check for existing records
TABLE_ID: Table ID to check for existing records
'''


def get_pems_data(days_to_fetch=None):
    if days_to_fetch is None:
        days_to_fetch = [(datetime.now(ZoneInfo("America/Los_Angeles")) - timedelta(days=1)).strftime('%Y_%m_%d')]

    session = requests.Session()
    # Log in
    session.post(
        BASE_URL,
        data={
            "username": os.environ['USERNAME'],
            "password": os.environ['PASSWORD'],
            "login": "Login",
        },
    )

    months = session.get(BASE_URL, params={"srq": "clearinghouse",
                                           "district_id": 4,
                                           "yy": 2024,
                                           "type": "station_5min",
                                           "returnformat": "text"})
    months.raise_for_status()

    for files in months.json()['data'].values():
        for file in files:
            if any(day in file['file_name'] for day in days_to_fetch):
                gzipped_data = session.get(BASE_URL + file['url'])
                gzipped_data.raise_for_status()
                data = gzip.decompress(gzipped_data.content)
                print(data)


def parse_int(val: str):
    return int(val) if len(val) > 0 else None


def parse_float(val: str):
    return float(val) if len(val) > 0 else None


def upload_to_bigquery():
    client = bigquery.Client(project="cloud-city-cal")
    job_config = bigquery.LoadJobConfig(schema=client.get_table("cloud_city.pems").schema)
    data = []

    with gzip.open("sample.txt.gz", "rt") as f:
        reader = csv.reader(f, delimiter=",")
        for row in tqdm.tqdm(reader):
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
                    continue # empty record

                pems.lanes.append(
                    PeMS.Lane(
                        samples=parse_int(row[offset + i * 5 + 0]),
                        flow=parse_int(row[offset + i * 5 + 1]),
                        average_occupancy=parse_float(row[offset + i * 5 + 2]),
                        average_speed=parse_float(row[offset + i * 5 + 3]),
                        observed=parse_int(row[offset + i * 5 + 4]) == 1
                    ))

            data.append(json_format.MessageToDict(pems, preserving_proto_field_name=True))

    client.load_table_from_json(
        data,
        "cloud_city.pems", job_config=job_config).result()
    exit()


#     publisher_client = PublisherClient()
#     topic_path = publisher_client.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_ID'])
#
#     # Crawl Data
#     for station_id in stations:
#         print(f"Fetching data for station_id: {station_id}.")
#         params = {
#             "report_form": 1,
#             "dnode": "VDS",
#             "content": "loops",
#             "export": "text",
#             "station_id": station_id,
#             "s_time_id": timestamp_now - TIME_RANGE,
#             "e_time_id": timestamp_now,
#             "dow_0": "on",
#             "dow_1": "on",
#             "dow_2": "on",
#             "dow_3": "on",
#             "dow_4": "on",
#             "dow_5": "on",
#             "dow_6": "on",
#             "dow_7": "on",
#             "holidays": "on",
#             "q": "speed",
#             "q2": "flow",
#             "gn": "5min",
#             "agg": "on",
#             "lane1": "on",
#             "lane2": "on",
#             "lane3": "on",
#             "lane4": "on",
#             "lane5": "on",
#             "lane6": "on",
#             "lane7": "on",
#         }
#         res = session.post(
#             BASE_URL,
#             params=params,
#         )
#         res.raise_for_status()
#         reader = csv.DictReader(StringIO(res.text), delimiter="\t", quoting=csv.QUOTE_NONE)
#         for row in reader:
#             lanes_len = int(row["# Lane Points"])
#             data = PeMS(station_id=station_id, time=row["5 Minutes"], observed=float(row["% Observed"]), lanes=[])
#             for i in range(1, lanes_len + 1):
#                 data.lanes.append(PeMS.Lane(speed=float(row[f"Lane {i} Speed (mph)"]),
#                                             flow=float(row[f"Lane {i} Flow (Veh/5 Minutes)"])))
#             publisher_client.publish(topic_path, data.SerializeToString())
#
#
# def get_missing_record_ids() -> List:
#     client = bigquery.Client(project=os.environ['PROJECT_ID'])
#
#     query_job = client.query(
#         f"""
#         SELECT station_id, MAX(`time`) as lastest_time
#         FROM {os.environ['PROJECT_ID']}.{os.environ['DATASET_ID']}.{os.environ['TABLE_ID']}
#         GROUP BY station_id
#         """)
#
#     return query_job.result()


if __name__ == '__main__':
    upload_to_bigquery()
