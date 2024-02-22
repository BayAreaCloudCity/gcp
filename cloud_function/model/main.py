import base64
import os
import numpy as np

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import pubsub

from bigquery.metadata import get_metadata
from pubsub.processed_pb2 import Processed
from pubsub.result_pb2 import Result

'''
Environment Variables:
PROJECT_ID: Current project ID
TOPIC_ID: Topic ID of the published message
'''

@functions_framework.cloud_event
def entrypoint(cloud_event: CloudEvent):
    print(cloud_event.data)
    processed = Processed()
    processed.ParseFromString(base64.b64decode(cloud_event.data['message']['data']))
    metadata_version = int(os.environ['METADATA_VERSION'])

    if metadata_version != processed.metadata_version:
        raise Exception("metadata version mismatch")

    model = get_metadata(metadata_version)['model']
    output = np.dot(processed.coefficients, model)

    result = Result(output=output, metadata_version=processed.metadata_version, segment_id=processed.segment_id, timestamp=processed.segment_id)
    publisher_client = pubsub.PublisherClient()
    topic_path = publisher_client.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_ID'])
    publisher_client.publish(topic_path, result.SerializeToString())

