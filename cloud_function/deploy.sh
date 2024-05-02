#!/bin/bash
# You'll need to create yaml files containing the environment variables in ../.config folder.

cd "$(dirname "$0")" || exit 1
cd ..

gcloud functions deploy data-collection_bay_area_511_event \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_publish_bay_area_511_event \
  --memory=256MiB \
  --cpu=0.167 \
  --env-vars-file=.config/cf_publish_bay_area_511_event.yaml \
  --trigger-topic=scheduler.BayArea511DataCollectionScheduledEvent

gcloud functions deploy data-collection-weather-2 \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_publish_weather \
  --memory=256MiB \
  --cpu=0.167 \
  --env-vars-file=.config/cf_publish_weather.yaml \
  --trigger-topic=scheduler.WeatherDataCollectionScheduledEvent

gcloud functions deploy data-collection-pems \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_collect_pems \
  --memory=8GiB \
  --cpu=2 \
  --env-vars-file=.config/cf_collect_pems.yaml \
  --timeout 540 \
  --trigger-topic=scheduler.PeMSDataCollectionScheduledEvent

gcloud functions deploy model \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_predict \
  --memory=512MiB \
  --cpu=0.333 \
  --env-vars-file=.config/cf_predict.yaml \
  --trigger-http

gcloud functions deploy replayer \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_replay_from_bigquery \
  --memory=512MiB \
  --cpu=0.167 \
  --env-vars-file=.config/cf_replay_from_bigquery.yaml \
  --trigger-topic=replayer.TriggeredEvent


gcloud functions deploy cf_preprocess \
  --gen2 \
  --region=us-west1 \
  --runtime=python311 \
  --source=. \
  --entry-point=cf_preprocess \
  --memory=4GiB \
  --cpu=2 \
  --env-vars-file=.config/cf_preprocess.yaml \
  --timeout 540 \
  --trigger-topic=scheduler.PreprocessingTriggerEvent
