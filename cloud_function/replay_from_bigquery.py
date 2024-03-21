import os
from datetime import datetime, timedelta
from typing import TypedDict, List
from zoneinfo import ZoneInfo

from google.cloud import bigquery, pubsub, scheduler
from google.protobuf import json_format

QUERY = "SELECT * FROM {} WHERE publish_time > @start AND publish_time < @end"
CURRENT_TIMEZONE = ZoneInfo("America/Los_Angeles")


class DataSourceConfig(TypedDict):
    table_name: str  # big query table to read data from
    proto_package: str  # package containing protobuf definitions
    proto_class: str  # class of the protobuf message
    topic_id: str  # topic ID for the replayed data
    fetch_interval: int  # duration, in minutes, before the simulation's current time for range queries.


class TimeConfig:
    simulation_start_time: datetime
    """datetime object marking the start of the simulated timeline.
    This is the point in the simulated environment from which the streaming begins."""
    simulation_end_time: datetime
    """datetime object indicating the end of the simulated timeline.
      It defines when the simulation should stop, synchronizing with simulation_start_time to outline the simulation 
      duration."""
    real_start_time: datetime
    """datetime object specifying the real-world start time of the simulation.
      # This aligns the beginning of the simulation with a real-world moment, acting as a reference point for 
      synchronization between real time and simulated time."""
    speed: int
    """int defining the playback speed of the simulation. This variable determines how quickly simulated time advances in 
    comparison to real time.
      A higher speed means the simulation covers the period between simulation_start_time and simulation_end_time faster. """
    scheduler_name: str  # name of the scheduler responsible for trigerring this simulation

    def __init__(self, simulation_start_time: datetime, simulation_end_time: datetime, real_start_time: datetime,
                 scheduler_name: str, speed: int):
        self.simulation_start_time = simulation_start_time
        self.simulation_end_time = simulation_end_time
        self.real_start_time = real_start_time
        self.scheduler_name = scheduler_name
        self.speed = speed

    def is_before_simulation(self, time: datetime):
        return self.get_simulation_time(time) < self.simulation_start_time

    def is_after_simulation(self, time: datetime):
        return self.get_simulation_time(time) > self.simulation_end_time

    def get_simulation_time(self, time: datetime):
        return self.simulation_start_time + (time - self.real_start_time) * self.speed

    def get_scheduler_name(self):
        return self.scheduler_name


def replay_config(config: DataSourceConfig, time: datetime):
    # range query all data within interval
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start", "INT64", int((time - timedelta(minutes=config['fetch_interval'])).timestamp() * 1e6)),
            bigquery.ScalarQueryParameter("end", "INT64", int(time.timestamp() * 1e6)),
        ]
    )

    bigquery_client = bigquery.Client(project=os.environ['PROJECT_ID'])
    pubsub_client = pubsub.PublisherClient()

    query_job = bigquery_client.query(QUERY.format(config['table_name']), job_config=job_config)
    count = 0

    mod = __import__(config['proto_package'])
    message_type = getattr(mod, config['proto_class'])

    for row in query_job.result():
        # map to ProtoBuf and send them out
        message = message_type()
        proto = json_format.ParseDict(dict(row), message, ignore_unknown_fields=True)
        pubsub_client.publish(config['topic_id'], proto.SerializeToString())
        count += 1

    print(f"Replayed {count} rows from {config['table_name']}.")


def replay_from_bigquery(time_config: TimeConfig, data_source_config: List[DataSourceConfig]):
    now = datetime.now(CURRENT_TIMEZONE)
    time = time_config.get_simulation_time(now)
    print(f"Current time {now} in simulation is {time}.")

    if time_config.is_before_simulation(now):
        # do nothing if the simulation has not started
        return

    if time_config.is_after_simulation(now):
        #  turn off scheduler if simulation is done
        scheduler_client = scheduler.CloudSchedulerClient()
        scheduler_client.pause_job(name=time_config.get_scheduler_name())
        return

    for ds in data_source_config:
        replay_config(ds, time)
