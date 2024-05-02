# Cloud City *on Google Cloud Platform*

This project is our reference implementation of using Google Cloud Platform to build a smart city application.

## Setup

- **BigQuery**: Create BigQuery datasets and tables using the schema in the `pubsub` folder. A snapshot of the configs can be found in `.tf` folder.
- **PubSub**: Create topics using schemas in the `pubsub` folder, and connect relevant topics to BigQuery. A snapshot of the configs can be found in `.tf` folder.
- **Cloud Function**: Follow `cloud_function/deploy.sh` on how to deploy the file.
- **Cloud Run**: Follow `cloud_run/deploy.sh` on how to deploy the file.