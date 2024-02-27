#!/bin/bash

timestamp=$(date +%s)

zip -r /tmp/"$timestamp".zip . -x "venv/*" ".git/*" ".idea/*"
gcloud storage cp /tmp/"$timestamp".zip gs://cloud-city/gcp.git
