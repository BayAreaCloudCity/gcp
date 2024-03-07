"""
This file dispatches Cloud Function calls to its corresponding modules.
"""
from datetime import datetime

import functions_framework
from cloudevents.http import CloudEvent
from flask import Request

from cloud_function.predict import predict
from cloud_function.replay_from_bigquery import replay_from_bigquery
from cloud_function.publish_pems import collect_pems
from cloud_function.publish_bay_area_511_event import publish_bay_area_511_event
from cloud_function.publish_weather import publish_weather


@functions_framework.http
def predict(request: Request):
    return predict(request)


@functions_framework.cloud_event
def cf_replay_from_bigquery(cloud_event: CloudEvent):
    """
    This Cloud Function simulates real-time streaming using previously stored PubSub messages in BigQuery.
    It maps current time to simulation time, with adjustable playback speed, using the attributes defined in the event.
    Then, it performs range query in BigQuery, and re-publishes them to PubSub topics.
    Only minimal CPU (0.333) and memory (256 MiB) is needed, and can be scheduled in any time interval using a Cloud
    Scheduler.

    Required cloud scheduler attributes:
    - simulation_config: A JSON representation of the Simulation object, which specifies the simulation time conversion.
    - replay_config: A JSON representation of one or more Replay object, which specifies which topics and tables to replay.
    """
    replay_from_bigquery(Simulation(
        simulation_start_time=datetime.fromisoformat(
            cloud_event.data['message']['attributes']['simulation_start_time']),
        simulation_end_time=datetime.fromisoformat(cloud_event.data['message']['attributes']['simulation_end_time']) if
        'simulation_end_time' in cloud_event.data['message']['attributes'] else datetime.now(CURRENT_TIMEZONE),
        real_start_time=datetime.fromisoformat(cloud_event.data['message']['attributes']['real_start_time']),
        speed=int(cloud_event.data['message']['attributes']['speed'])
    ))


@functions_framework.cloud_event
def cf_collect_pems(cloud_event: CloudEvent):
    """
    This cloud function collects the previous day's PeMS data, and stores them into a BigQuery table.
    Some CPU (2) and a large memory (8 GiB) is needed due to the need to hold a full day's data, but only need be
    scheduled only once per day per district (to avoid duplicate data).
    To get realtime data from PeMS using FTP, you may need to apply the access through their website.

    Required environment variables:
    - USERNAME: Username for pems.dot.ca.gov
    - PASSWORD: Password for pems.dot.ca.gov
    - DISTRICT_ID: CalTrans district ID where data should be downloaded
    - DATASET_ID: BigQuery dataset ID to insert records into
    - TABLE_ID: BigQuery table ID to insert records into
    """
    collect_pems()


@functions_framework.cloud_event
def cf_publish_bay_area_511_event(cloud_event: CloudEvent):
    """
    This Cloud Function collects all current active events on 511.org, and publishes them to a PubSub topic.
    Only minimal CPU (0.333) and memory (256 MiB) is needed, and can be scheduled in any time interval (10 minutes
    preferred) using a Cloud Scheduler.

    Required environment variables:
    - API_KEY: API Key for 511.org
    - TOPIC_ID: Topic ID of the published message
    """
    publish_bay_area_511_event()


@functions_framework.cloud_event
def cf_publish_weather(cloud_event: CloudEvent):
    """
    This cloud function collects current weather data from openweatherapi.org for each of the coordinates defined in the
    metadata, and publishes them to a PubSub topic.
    Only minimal CPU (0.333) and memory (256 MiB) is needed, and can be scheduled in any time interval (10 minutes
    preferred) using a Cloud Scheduler.

    Required environment variables:
    - API_KEY: API Key for openweathermap.org
    - TOPIC_ID: Topic ID of the published message
    - CONFIG_VERSION: Version of the metadata to use
    """
    publish_weather()
