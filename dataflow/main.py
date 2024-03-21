import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

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


def get_table_query(table_name: str, start: datetime, end: datetime, buffer: timedelta):
    """Fetch data with extra buffer added to count for windowing, so that at start time, enough data is available."""
    return (f"SELECT * FROM `{os.environ['PROJECT_ID']}.{os.environ['DATASET_ID']}.{table_name}` "
            f"WHERE publish_time >= {int((start - buffer).timestamp() * 1e6)} AND publish_time < {int(end.timestamp() * 1e6)}")


def get_tabel_spec(table_name: str):
    return bigquery.TableReference(
        projectId=os.environ['PROJECT_ID'],
        datasetId=os.environ['DATASET_ID'],
        tableId=table_name)


def run(start: datetime, end: datetime, metadata_version: int,
        bay_area_511_event_table: str, pems_table: str, weather_table: str,
        output_table: Optional[str],
        window_size: int = 900, window_period: int = 300, pipeline_args=None):
    print(
        f"Processing data from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')} using metadata v{metadata_version}. "
        f"Output to BigQuery: {output_table}.")
    pipeline_options = PipelineOptions(
        pipeline_args, save_main_session=True, project=os.environ['PROJECT_ID']
    )

    segments = get_metadata(metadata_version)['segments']

    with Pipeline(options=pipeline_options) as pipeline:
        window = SlidingWindows(window_size, window_period)
        # Note: for streaming mode, read from PubSub instead of BigQuery.
        bay_area_511_event: PCollection = (
                pipeline
                | "511.org Events: Read" >> io.ReadFromBigQuery(
            query=get_table_query(bay_area_511_event_table, start, end, window_size), use_standard_sql=True)
                | "511.org Events: Map to Segments" >> ParDo(BayArea511EventTransformDoFn(segments))
                | '511.org Events: Window' >> WindowInto(window)
        )

        pems: PCollection = (
                pipeline
                | "PeMS: Read" >> io.ReadFromBigQuery(
            query=get_table_query(pems_table, start, end, window_size), use_standard_sql=True)
                | "PeMS: Map to Segments" >> ParDo(PeMSTransformDoFn(segments))
                | 'PeMS: Window' >> WindowInto(window)
        )

        weather: PCollection = (
                pipeline
                | "Weather: Read" >> io.ReadFromBigQuery(
            query=get_table_query(weather_table, start, end, window_size), use_standard_sql=True)
                | "Weather: Map to Segments" >> ParDo(WeatherTransformDoFn(segments))
                | 'Weather: Window' >> WindowInto(window)
        )

        result: PCollection = (({
            'bay_area_511_event': bay_area_511_event, 'weather': weather, 'pems': pems
        })
                               | 'Merge by Segment' >> CoGroupByKey()
                               | 'Feature Transform' >> ParDo(SegmentFeatureTransformDoFn(segments, metadata_version))
                               | 'Discard Buffer' >> Filter(
                    lambda row: start.timestamp() <= row['timestamp'] < end.timestamp()))

        if output_table is not None:
            (result
             | 'Write to BigQuery' >> io.WriteToBigQuery(
                        table=get_tabel_spec(output_table),
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
        "--bay_area_511_event_table",
        help="BigQuery table to read 511.org events data from.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--pems_table",
        help="BigQuery table to read PeMS data from.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--weather_table",
        help="BigQuery table to read weather data from.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--output_table",
        help="BigQuery table to write output. If let unspecified, it will write to a local JSON file instead.",
        type=str,
        required=False,
        default=None
    )
    parser.add_argument(
        "--window_size",
        help="Window size. See Beam's documentation on SlidingWindows.",
        type=int,
        default=900,
        required=False
    )
    parser.add_argument(
        "--window_period",
        help="Window period. See Beam's documentation on SlidingWindows.",
        type=int,
        default=300,
        required=False
    )
    parser.add_argument(
        "--metadata_version",
        help="Version of the metadata to use.",
        type=int,
        required=True
    )

    args, beam_args = parser.parse_known_args()
    run(datetime.strptime(args.start, "%Y%m%d"),
        datetime.strptime(args.end, "%Y%m%d"),
        args.metadata_version,
        args.bay_area_511_event_table,
        args.pems_table,
        args.weather_table,
        args.output_table,
        args.window_size,
        args.window_period,
        beam_args)
