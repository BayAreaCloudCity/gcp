"""
This file dispatches Cloud Function calls to its corresponding modules.

Required environment variables for all Cloud Functions:
- METADATA_VERSION: Version of the metadata to use
- METADATA_DATASET_ID: Dataset where metadata is located
- PROJECT_ID: Project ID of GCP
"""
import json

import functions_framework
from cloudevents.http import CloudEvent
from flask import Request

from cloud_function.predict import predict
from cloud_function.preprocess import preprocess
from cloud_function.replay_from_bigquery import replay_from_bigquery, TimeConfig
from cloud_function.collect_pems import collect_pems
from cloud_function.publish_bay_area_511_event import publish_bay_area_511_event
from cloud_function.publish_weather import publish_weather
from pubsub.processed_pb2 import Processed


@functions_framework.http
def cf_predict(request: Request):
    """
    This Cloud Function generates PubSub messages of the prediction output by accepting pushes from PubSub with
    processed data.
    Only minimal CPU (0.333) and memory (256 MiB) is needed. This Cloud Function should NOT be scheduled on Cloud
    Scheduler. Instead, its URL should be the destination of a 'Push' subscription of the processed data PubSub topic.

    Required environment variables:
    - TOPIC_ID: Topic ID of the published message
    """
    processed = Processed()
    processed.ParseFromString(request.get_data())
    return predict(processed)


@functions_framework.cloud_event
def cf_preprocess(request: Request):
    """
    This cloud function pre-processes the previous day's data for model prediction, and stores them into BigQuery.
    Some CPU (2) and a large memory (8 GiB) is needed due to the need to hold a full day's data, but only need be
    scheduled only once per day (to avoid duplicate data) and after PeMS data has been collected.
    """
    return preprocess()


@functions_framework.cloud_event
def cf_replay_from_bigquery(cloud_event: CloudEvent):
    """
    This Cloud Function simulates real-time streaming using previously stored PubSub messages in BigQuery.
    It maps current time to simulation time, with adjustable playback speed, using the attributes defined in the event.
    Then, it performs range query in BigQuery, and re-publishes them to PubSub topics.
    Only minimal CPU (0.333) and memory (256 MiB) is needed, and can be scheduled in any time interval using a Cloud
    Scheduler.

    Required cloud scheduler attributes:
    - time_config: A JSON representation of the TimeConfig object, which specifies the simulation time conversion.
    - data_source_config: A JSON representation of one or more DataSourceConfig object, which specifies which topics and
                          tables to replay.
    """
    replay_from_bigquery(TimeConfig(**json.loads(cloud_event.data['time_config'])), json.loads(cloud_event.data['data_source_config']))


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
    """
    publish_weather()
