#!/bin/bash
# run this script to deploy the container to Google Cloud Artifact Registry
docker build . -t us-west1-docker.pkg.dev/cloud-city-cal/dashboard/grafana:latest
docker push us-west1-docker.pkg.dev/cloud-city-cal/dashboard/grafana:latest
gcloud run deploy grafana \
  --region=us-west1 \
  --image=us-west1-docker.pkg.dev/cloud-city-cal/dashboard/grafana:latest \
  --port=3000 \
  --memory=512M \
  --cpu=1
