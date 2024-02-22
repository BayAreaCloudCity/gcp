import argparse
import json
import logging
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from apache_beam import (
    io,
    Pipeline,
    Map, ParDo, CoGroupByKey, WindowInto
)
from apache_beam.io import WriteToText, BigQueryDisposition
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import PCollection
from apache_beam.transforms.window import SlidingWindows

from bigquery.metadata import get_metadata, get_schema
from dataflow.dofn import BayArea511EventTransformDoFn, PeMSTransformDoFn, WeatherTransformDoFn, \
    SegmentFeatureTransformDoFn


def get_tabel_spec(table_name: str, partition: int = None):
    return bigquery.TableReference(
        projectId='cloud-city-cal',
        datasetId='cloud_city',
        tableId=f"{table_name}${partition}" if partition is not None else f"{table_name}")


def run(partition: int, metadata_version: int, save_to_bigquery: bool, pipeline_args=None):
    print(f"Processing data for partition {partition} using metadata version {metadata_version}. "
          f"Output to BigQuery enabled: {save_to_bigquery}.")
    pipeline_options = PipelineOptions(
        pipeline_args, save_main_session=True, temp_location="gs://cloud-city/tmp"
    )

    segments = get_metadata(metadata_version)['segments']

    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(900, 300)
        bay_area_511_event: PCollection = (
                pipeline
                | "bay_area_511_event: Read" >> io.ReadFromBigQuery(
            table=get_tabel_spec("bay_area_511_event_partitioned", partition))
                | "bay_area_511_event: Map" >> ParDo(BayArea511EventTransformDoFn(segments))
                | 'bay_area_511_event: Window' >> WindowInto(window)
        )

        pems: PCollection = (
                pipeline
                | "pems: Read" >> io.ReadFromBigQuery(table=get_tabel_spec("pems_partitioned", partition))
                | "pems: Map" >> ParDo(PeMSTransformDoFn(segments))
                | 'pems: Window' >> WindowInto(window)
        )

        weather: PCollection = (
                pipeline
                | "weather: Read" >> io.ReadFromBigQuery(table=get_tabel_spec("weather_partitioned", partition))
                | "weather: Map" >> ParDo(WeatherTransformDoFn(segments))
                | 'weather: Window' >> WindowInto(window)
        )

        result: PCollection = (({
            'bay_area_511_event': bay_area_511_event, 'weather': weather, 'pems': pems
        })
                               | 'Merge' >> CoGroupByKey()
                               | 'Encode' >> ParDo(SegmentFeatureTransformDoFn(segments)))

        if save_to_bigquery:
            (result
             | 'bigquery: write' >> io.WriteToBigQuery(
                        table=get_tabel_spec("processed_partitioned"),
                        create_disposition=BigQueryDisposition.CREATE_NEVER,
                        write_disposition=BigQueryDisposition.WRITE_APPEND))

        else:
            (result
             | 'json: map' >> Map(json.dumps)
             | 'json: write' >> WriteToText(f"{partition}_{metadata_version}.json"))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        help="Date (YYYYMMDD) to process within its 24-hour period in Pacific Standard Time (not Daylight Saving).",
        type=str,
        required=True
    )
    parser.add_argument(
        "--metadata",
        help="Version of the metadata to use.",
        type=int,
        required=True
    )
    parser.add_argument(
        "--bigquery",
        help="Whether to write to bigquery or a local json file.",
        action='store_true',
        default=False
    )
    args, beam_args = parser.parse_known_args()
    partition = int(
        datetime.strptime(args.date, "%Y%m%d").replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp() * 1000000)
    run(partition, args.metadata, args.bigquery, beam_args)
