import json
import logging
import os

from apache_beam import (
    io,
    Pipeline,
    Map, ParDo, CoGroupByKey, WindowInto
)
from apache_beam.io import WriteToText
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import PCollection
from apache_beam.transforms.window import SlidingWindows

from bigquery.metadata import get_metadata
from dataflow.dofn import BayArea511EventTransformDoFn, PeMSTransformDoFn, WeatherTransformDoFn, \
    SegmentFeatureTransformDoFn

# PEMS_TABLE_SPEC = bigquery.TableReference(
#     projectId='cloud-city-cal',
#     datasetId='cloud_city',
#     tableId='pems_partitioned$1708243200000000')

WEATHER_TABLE_SPEC = bigquery.TableReference(
    projectId='cloud-city-cal',
    datasetId='cloud_city',
    tableId='weather_partitioned$1708243200000000')

BAY_AREA_511_EVENT_TABLE_SPEC = bigquery.TableReference(
    projectId='cloud-city-cal',
    datasetId='cloud_city',
    tableId='bay_area_511_event_partitioned$1708243200000000')

def run(pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True, temp_location="gs://cloud-city/tmp"
    )

    segments = get_metadata(int(os.environ['METADATA_VERSION']))

    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(900, 60)
        bay_area_511_event: PCollection = (
                pipeline
                | "bay_area_511_event: Read" >> io.ReadFromBigQuery(table=BAY_AREA_511_EVENT_TABLE_SPEC)
                | "bay_area_511_event: Map" >> ParDo(BayArea511EventTransformDoFn(segments))
                | 'bay_area_511_event: Window' >> WindowInto(window)
        )

        # pems: PCollection = (
        #         pipeline
        #         | "pems: Read" >> io.ReadFromBigQuery(table=PEMS_TABLE_SPEC)
        #         | "pems: Map" >> ParDo(PeMSTransformDoFn(segments))
        #         | 'pems: Window' >> WindowInto(window)
        # )

        weather: PCollection = (
                pipeline
                | "weather: Read" >> io.ReadFromBigQuery(table=WEATHER_TABLE_SPEC)
                | "weather: Map" >> ParDo(WeatherTransformDoFn(segments))
                | 'weather: Window' >> WindowInto(window)
        )

        (({
            'bay_area_511_event': bay_area_511_event, 'weather': weather
        })
         | 'Merge' >> CoGroupByKey()
         | 'Encode' >> ParDo(SegmentFeatureTransformDoFn(segments))
         | 'JSON' >> Map(json.dumps)
         | 'Write' >> WriteToText("output.json")
         )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.ERROR)
    run()
