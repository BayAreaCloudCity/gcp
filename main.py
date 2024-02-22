import functions_framework
from cloudevents.http import CloudEvent

from cloud_function.replayer.main import entrypoint as replayer_entrypoint
from cloud_function.model.main import entrypoint as model_entrypoint


@functions_framework.cloud_event
def replayer(cloud_event: CloudEvent):
    replayer_entrypoint(cloud_event)


@functions_framework.http
def model(cloud_event: CloudEvent):
    model_entrypoint(cloud_event)
