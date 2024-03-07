import os

import numpy as np
from flask import Request
from google.cloud import pubsub

from bigquery.metadata import get_metadata
from pubsub.processed_pb2 import Processed
from pubsub.result_pb2 import Result


def predict(request: Request):
    processed = Processed()
    processed.ParseFromString(request.get_data())
    metadata_version = int(os.environ['METADATA_VERSION'])

    if metadata_version != processed.metadata_version:
        raise Exception("metadata version mismatch")

    model = get_metadata(metadata_version)['model']
    output = np.dot(processed.coefficients, model)

    result = Result(output=output, metadata_version=processed.metadata_version, segment_id=processed.segment_id, timestamp=processed.timestamp)
    publisher_client = pubsub.PublisherClient()
    topic_path = publisher_client.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_ID'])
    publisher_client.publish(topic_path, result.SerializeToString())

    return "OK", 200