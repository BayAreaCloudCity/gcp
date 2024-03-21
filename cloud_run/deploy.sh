#!/bin/bash

docker build . -t us-west1-docker.pkg.dev/cloud-city-cal/dashboard/grafana:latest
docker push us-west1-docker.pkg.dev/cloud-city-cal/dashboard/grafana:latest