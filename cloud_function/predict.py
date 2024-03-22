import os

import numpy as np
from google.cloud import pubsub

from bigquery.metadata import get_metadata
from pubsub.processed_pb2 import Processed
from pubsub.result_pb2 import Result

METADATA_CACHE = None


def predict(processed: Processed):
    metadata_version = int(os.environ['METADATA_VERSION'])

    if metadata_version != processed.metadata_version:
        raise Exception("metadata version mismatch")

    model = get_metadata(metadata_version)['model']
    output = np.dot(processed.coefficients, model)  # linear regression is just a dot product between coef and input.

    result = Result(output=output, metadata_version=processed.metadata_version, segment_id=processed.segment_id,
                    timestamp=processed.timestamp)
    publisher_client = pubsub.PublisherClient()
    topic_path = publisher_client.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_ID'])
    publisher_client.publish(topic_path, result.SerializeToString())

    return "OK", 200
