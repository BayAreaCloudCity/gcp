import logging
import os

from apache_beam import (
    io,
    Pipeline,
    Map, ParDo, CoGroupByKey, WindowInto
)
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import PCollection
from apache_beam.transforms.window import SlidingWindows

from bigquery.metadata import get_metadata
from dataflow.dofn import BayArea511EventTransformDoFn, PeMSTransformDoFn, WeatherTransformDoFn, \
    SegmentFeatureTransformDoFn


def run(pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    segments = get_metadata(int(os.environ['METADATA_VERSION']))

    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(900, 60)
        bay_area_511_event: PCollection = (
                pipeline
                | "bay_area_511_event: Read" >> io.ReadFromPubSub(
            subscription='projects/cloud-city-cal/subscriptions/preprocessor.bay_area_511_event.replayed')
                | "bay_area_511_event: Map" >> ParDo(BayArea511EventTransformDoFn(segments))
                | 'bay_area_511_event: Window' >> WindowInto(window)
        )

        pems: PCollection = (
                pipeline
                | "pems: Read" >> io.ReadFromPubSub(
            subscription='projects/cloud-city-cal/subscriptions/preprocessor.pems.replayed')
                | "pems: Map" >> ParDo(PeMSTransformDoFn(segments))
                | 'pems: Window' >> WindowInto(window)
        )

        weather: PCollection = (
                pipeline
                | "weather: Read" >> io.ReadFromPubSub(
            subscription='projects/cloud-city-cal/subscriptions/preprocessor.weather.replayed')
                | "weather: Map" >> ParDo(WeatherTransformDoFn(segments))
                | 'weather: Window' >> WindowInto(window)
        )

        (({
            'bay_area_511_event': bay_area_511_event, 'pems': pems, 'weather': weather
        })
         | 'Merge' >> CoGroupByKey()
         | 'Encode' >> ParDo(SegmentFeatureTransformDoFn(segments))
         | 'Write' >> Map(print)
         )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.ERROR)
    run()
