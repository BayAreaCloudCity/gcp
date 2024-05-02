import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from dataflow.main import run


def preprocess():
    midnight = datetime.combine(datetime.now(ZoneInfo("America/Los_Angeles")), time.min)
    run(
        start=midnight - timedelta(days=2), end=midnight - timedelta(days=1),
        metadata_version=int(os.environ['METADATA_VERSION']),
        bay_area_511_event_table=os.environ['BAY_AREA_511_EVENT_TABLE_ID'],
        pems_table=os.environ['PEMS_TABLE_ID'],
        weather_table=os.environ['WEATHER_TABLE_ID'],
        output_table=os.environ['OUTPUT_TABLE_ID'],
        pipeline_args=["--temp_location", os.environ['TEMP_LOCATION']]
    )
