import os

import requests
from cloudevents.http import CloudEvent
from google.cloud import pubsub
from google.protobuf.json_format import ParseDict

from bigquery.metadata import get_metadata
from pubsub.weather_pb2 import Weather

API_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"


def publish_weather():
    for segment in get_metadata(int(os.environ['METADATA_VERSION']))['segments']:
        lat = segment["representative_point"][0]
        lon = segment["representative_point"][1]

        response = requests.get(API_ENDPOINT, params={
            "lon": lon,
            "lat": lat,
            "appid": os.environ['API_KEY'],
            "units": "metric",
        })
        response.raise_for_status()
        proto = ParseDict(response.json(), Weather())

        publisher_client = pubsub.PublisherClient()
        topic_path = publisher_client.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_ID'])
        publisher_client.publish(topic_path, proto.SerializeToString())
