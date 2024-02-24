import base64
import os
from datetime import datetime, timedelta
from typing import TypedDict
from zoneinfo import ZoneInfo

import google.protobuf.message
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub
from google.protobuf import json_format

from cloud_function.util.simulation import Simulation
from pubsub.processed_pb2 import Processed

QUERY = "SELECT * FROM {} WHERE publish_time > @start AND publish_time < @end"
CURRENT_TIMEZONE = ZoneInfo("America/Los_Angeles")


class Config(TypedDict):
    table_name: str
    proto_type: type[google.protobuf.message.Message]
    topic_id: str
    fetch_interval: timedelta


CONFIG = [
    Config(table_name="cloud_city.processed_partitioned", proto_type=Processed,
           topic_id="projects/cloud-city-cal/topics/model.input", fetch_interval=timedelta(minutes=5)),
]

'''
Environment Variables:
PROJECT_ID: Current project ID
'''


def replay_pubsub(cloud_event: CloudEvent):
    replay(Simulation(
        simulation_start_time=datetime.fromisoformat(cloud_event.data['message']['attributes']['simulation_start_time']),
        simulation_end_time=datetime.fromisoformat(cloud_event.data['message']['attributes']['simulation_end_time']) if
        'simulation_end_time' in cloud_event.data['message']['attributes'] else datetime.now(CURRENT_TIMEZONE),
        real_start_time=datetime.fromisoformat(cloud_event.data['message']['attributes']['real_start_time']),
        speed=int(cloud_event.data['message']['attributes']['speed'])
    ))


def replay_config(config: Config, time: datetime):
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start", "INT64", int((time - config['fetch_interval']).timestamp() * 1e6)),
            bigquery.ScalarQueryParameter("end", "INT64", int(time.timestamp() * 1e6)),
        ]
    )

    bigquery_client = bigquery.Client(project=os.environ['PROJECT_ID'])
    pubsub_client = pubsub.PublisherClient()

    query_job = bigquery_client.query(QUERY.format(config['table_name']), job_config=job_config)
    count = 0

    for row in query_job.result():
        message = config['proto_type']()
        proto = json_format.ParseDict(dict(row), message, ignore_unknown_fields=True)
        print(base64.b64encode(message.SerializeToString()))
        pubsub_client.publish(config['topic_id'], proto.SerializeToString())
        count += 1

    print(f"Replayed {count} rows from {config['table_name']}.")


def turn_off_scheduler():
    pass  # TODO: Turn off scheduler


def replay(simulation: Simulation):
    now = datetime.now(CURRENT_TIMEZONE)
    time = simulation.get_simulation_time(now)
    print(f"Current time {now} in simulation is {time}.")

    if simulation.is_before_simulation(now):
        return

    if simulation.is_after_simulation(now):
        turn_off_scheduler()
        return

    for config in CONFIG:
        replay_config(config, time)
