resource "google_pubsub_subscription" "eventarc_us_west1_data_collection_pems_655802_sub_491" {
  ack_deadline_seconds = 600

  labels = {
    goog-drz-eventarc-location = "us-west1"
    goog-eventarc              = ""
    goog-drz-eventarc-uuid     = "dcd971ac-5e9e-4228-86d8-9c3d31b1c47f"
  }

  message_retention_duration = "86400s"
  name                       = "eventarc-us-west1-data-collection-pems-655802-sub-491"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      audience              = "https://data-collection-pems-et73rt2k6a-uw.a.run.app"
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://data-collection-pems-et73rt2k6a-uw.a.run.app?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fcloud-city-cal%2Ftopics%2Fscheduler.PeMSDataCollectionScheduledEvent"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/scheduler.PeMSDataCollectionScheduledEvent"
}
# terraform import google_pubsub_subscription.eventarc_us_west1_data_collection_pems_655802_sub_491 projects/cloud-city-cal/subscriptions/eventarc-us-west1-data-collection-pems-655802-sub-491
