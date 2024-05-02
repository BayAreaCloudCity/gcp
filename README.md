# Cloud City on Google Cloud Platform

This project is our reference implementation of using Google Cloud Platform to build a smart city application. It demonstrates how to leverage cloud technology to manage IoT data effectively. For more details, please visit our [home page](https://github.com/BayAreaCloudCity).


![image](https://github.com/BayAreaCloudCity/gcp/assets/12138874/a2f5f09a-c6ee-40bd-8ff6-7c52d0bbc864)



## Setup

- **BigQuery**: Create BigQuery datasets and tables using the schema in the `pubsub` folder. A snapshot of the configuration files (Terraform scripts) can be found in the `.tf` folder.
- **PubSub**: Create topics using schemas in the `pubsub` folder, and connect relevant topics to BigQuery. A snapshot of the configuration files can be found in the `.tf` folder.
- **Cloud Function**: Follow the steps in `cloud_function/deploy.sh` to deploy the Cloud Function.
- **Cloud Run**: Follow the steps in `cloud_run/deploy.sh` to deploy the application on Cloud Run.

## Reference Architecture


![Acrobat_OdcqMPXyql](https://github.com/BayAreaCloudCity/gcp/assets/12138874/3230853e-6441-4a26-8f09-8b4fdb5ac21b)
