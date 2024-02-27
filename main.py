"""
This file dispatches Cloud Function calls to its corresponding modules.
"""
import functions_framework
from cloudevents.http import CloudEvent
from flask import Request

from cloud_function.predict import predict
from cloud_function.replay_pubsub import replay_pubsub
from cloud_function.collect_pems import collect_pems
from cloud_function.collect_bay_area_511_event import collect_bay_area_511_event
from cloud_function.collect_weather import collect_weather


@functions_framework.http
def predict(request: Request):
    return predict(request)


@functions_framework.cloud_event
def replay_pubsub(cloud_event: CloudEvent):
    replay_pubsub(cloud_event)


@functions_framework.cloud_event
def collect_pems(cloud_event: CloudEvent):
    collect_pems(cloud_event)


@functions_framework.cloud_event
def collect_bay_area_511_event(cloud_event: CloudEvent):
    collect_bay_area_511_event(cloud_event)


@functions_framework.cloud_event
def collect_weather(cloud_event: CloudEvent):
    collect_weather(cloud_event)
