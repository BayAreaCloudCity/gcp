import argparse
import json
import logging
from datetime import datetime, timedelta

from apache_beam import (
    io,
    Pipeline,
    Map, ParDo, CoGroupByKey, WindowInto, Filter
)
from apache_beam.io import WriteToText, BigQueryDisposition
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import PCollection
from apache_beam.transforms.window import SlidingWindows

from bigquery.metadata import get_metadata
from dataflow.dofn import BayArea511EventTransformDoFn, PeMSTransformDoFn, WeatherTransformDoFn, \
    SegmentFeatureTransformDoFn

WINDOW_SIZE = timedelta(seconds=900)
WINDOW_PERIOD = timedelta(seconds=300)


def get_table_query(table_name: str, start: datetime, end: datetime, buffer: timedelta):
    return (f"SELECT * FROM `cloud-city-cal.cloud_city.{table_name}` "
            f"WHERE publish_time >= {int((start - buffer).timestamp() * 1e6)} AND publish_time < {int(end.timestamp() * 1e6)}")


def get_tabel_spec(table_name: str):
    return bigquery.TableReference(
        projectId='cloud-city-cal',
        datasetId='cloud_city',
        tableId=table_name)


def run(start: datetime, end: datetime, metadata_version: int, save_to_bigquery: bool, pipeline_args=None):
    print(
        f"Processing data from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')} using metadata v{metadata_version}. "
        f"Output to BigQuery enabled: {save_to_bigquery}.")
    pipeline_options = PipelineOptions(
        pipeline_args, save_main_session=True, temp_location="gs://cloud-city/tmp", project="cloud-city-cal"
    )

    segments = get_metadata(metadata_version)['segments']

    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(WINDOW_SIZE.seconds, WINDOW_PERIOD.seconds)
        bay_area_511_event: PCollection = (
                pipeline
                | "511.org Events: Read" >> io.ReadFromBigQuery(
            query=get_table_query("bay_area_511_event_partitioned", start, end, WINDOW_SIZE), use_standard_sql=True)
                | "511.org Events: Map to Segments" >> ParDo(BayArea511EventTransformDoFn(segments))
                | '511.org Events: Window' >> WindowInto(window)
        )

        pems: PCollection = (
                pipeline
                | "PeMS: Read" >> io.ReadFromBigQuery(
            query=get_table_query("pems_partitioned", start, end, WINDOW_SIZE), use_standard_sql=True)
                | "PeMS: Map to Segments" >> ParDo(PeMSTransformDoFn(segments))
                | 'PeMS: Window' >> WindowInto(window)
        )

        weather: PCollection = (
                pipeline
                | "Weather: Read" >> io.ReadFromBigQuery(
            query=get_table_query("weather_partitioned", start, end, WINDOW_SIZE), use_standard_sql=True)
                | "Weather: Map to Segments" >> ParDo(WeatherTransformDoFn(segments))
                | 'Weather: Window' >> WindowInto(window)
        )

        result: PCollection = (({
            'bay_area_511_event': bay_area_511_event, 'weather': weather, 'pems': pems
        })
                               | 'Merge by Segment' >> CoGroupByKey()
                               | 'Feature Transform' >> ParDo(SegmentFeatureTransformDoFn(segments, metadata_version))
                               | 'Discard Buffer' >> Filter(lambda row: start.timestamp() <= row['timestamp'] < end.timestamp()))

        if save_to_bigquery:
            (result
             | 'Write to BigQuery' >> io.WriteToBigQuery(
                        table=get_tabel_spec("processed_partitioned"),
                        create_disposition=BigQueryDisposition.CREATE_NEVER,
                        write_disposition=BigQueryDisposition.WRITE_APPEND))

        else:
            (result
             | 'Map to JSON' >> Map(json.dumps)
             | 'Save as Local File' >> WriteToText(
                        f"{start.strftime('%Y-%m-%d')}_{end.strftime('%Y-%m-%d')}_v{metadata_version}.json"))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        help="Date (YYYYMMDD) to start process at its 12:00AM in UTC Time (inclusive).",
        type=str,
        required=True
    )
    parser.add_argument(
        "--end",
        help="Date (YYYYMMDD) to end process at its 12:00AM in UTC Time (exclusive).",
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
    run(datetime.strptime(args.start, "%Y%m%d"),
        datetime.strptime(args.end, "%Y%m%d"),
        args.metadata,
        args.bigquery,
        beam_args)
