import logging
from typing import List

from apache_beam import (
    io,
    Pipeline,
    Map, ParDo, CoGroupByKey, WindowInto
)
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import PCollection, DoOutputsTuple
from apache_beam.transforms.window import SlidingWindows
from google.cloud import bigquery

from dataflow.pubsub_parser import BayArea511EventTransformDoFn, PeMSTransformDoFn, WeatherTransformDoFn, \
    SegmentFeatureTransformDoFn
from dataflow.segment_definition import SegmentDefinition


def get_conf() -> List[SegmentDefinition]:
    client = bigquery.Client(project="cloud-city-cal")
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("version", "INT64", 2)
        ],
    )

    query_job = client.query(
        f"""
            SELECT *
            FROM `cloud_city.metadata`
            WHERE version = @version
            """, job_config=job_config)

    result = query_job.result(max_results=1)
    return next(result).data


def run(pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    segments = get_conf()
    segment_ids = [str(segment['id']) for segment in segments]


    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(900, 60)
        bay_area_511_event: PCollection = (
                pipeline
                | "bay_area_511_event: Read" >> io.ReadFromPubSub(subscription='projects/cloud-city-cal/subscriptions/preprocessor.bay_area_511_event.replayed')
                | "bay_area_511_event: Map" >> ParDo(BayArea511EventTransformDoFn(segments))
                | 'bay_area_511_event: window' >> WindowInto(window)
        )

        pems: PCollection = (
                pipeline
                | "pems: Read" >> io.ReadFromPubSub(subscription='projects/cloud-city-cal/subscriptions/preprocessor.pems.replayed')
                | "pems: Map" >> ParDo(PeMSTransformDoFn(segments))
                | 'pems: window' >> WindowInto(window)
        )

        weather: PCollection = (
                pipeline
                | "weather: Read" >> io.ReadFromPubSub(subscription='projects/cloud-city-cal/subscriptions/preprocessor.weather.replayed')
                | "weather: Map" >> ParDo(WeatherTransformDoFn(segments))
                | 'weather: window' >> WindowInto(window)
        )

        (({
            'bay_area_511_event': bay_area_511_event, 'pems': pems, 'weather': weather
        })
            | 'Merge' >> CoGroupByKey()
            | 'Encode' >> ParDo(SegmentFeatureTransformDoFn(segments))
            # | 'Write' >> io.WriteToPubSub()
        )




if __name__ == "__main__":
    logging.getLogger().setLevel(logging.ERROR)
    run()