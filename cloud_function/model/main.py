import base64
import os
import numpy as np

from flask import Request
from google.cloud import pubsub

from bigquery.metadata import get_metadata
from pubsub.processed_pb2 import Processed
from pubsub.result_pb2 import Result

'''
Environment Variables:
PROJECT_ID: Current project ID
TOPIC_ID: Topic ID of the published message
'''


def entrypoint(request: Request):
    print(request.get_data())
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

if __name__ == '__main__':
    metadata_version = 3
    os.environ['PROJECT_ID'] = 'cloud-city-cal'
    # model = get_metadata(metadata_version)['model']
    coef = [6.690837919129111,-1.9866058451056823e-11,7.01952542119821,-4.440892098500626e-15,-1.5987211554602254e-14,6.979125513250622,-0.06312528140456974,0.8257629088542646,1.7763568394002505e-15,3.2250868435029094,2.485968791142154,-6.217248937900877e-15,2.755283597173551,1.9984014443252818e-15,3.527571429612656,-1.7763568394002505e-15,2.6922292235924203,2.6645352591003757e-15,-8.881784197001252e-16,-1.7763568394002505e-15,4.996003610813204e-16,2.9235774413811155,3.079771527173002,2.4725056495311648e-05,3.0727289786168246,2.7723902385265986,2.785037671181999,2.7141852912675968,2.773234780516398,3.163875789805358,3.4080361036631013,-0.3263005746009946,-0.11013950406134387,-0.2749275191663736,-0.23147569659084466,-0.39376244109631936,-0.872912222352233,-1.507593428017504,-1.7003088985634816,-0.6827096744689427,-0.717625133436262,-1.4826468189923234,-1.5096507177583909,-2.0658934828496593,-3.9330773992414123,-4.790442954460837,-4.09331135913613,-4.821388033466075,-3.371625212395564,1.8917529407520264,1.2474376299324963,0.5477405285806445,-0.23481017503040413,-0.09812185868697174]
    output = np.dot(

        [0, 0, 0, 0, 0, 1, 0, 67.23430779, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 10000, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], coef)
    print(output)