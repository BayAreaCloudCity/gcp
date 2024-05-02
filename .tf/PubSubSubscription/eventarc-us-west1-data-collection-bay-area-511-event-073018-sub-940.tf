resource "google_pubsub_subscription" "eventarc_us_west1_data_collection_bay_area_511_event_073018_sub_940" {
  ack_deadline_seconds = 600

  labels = {
    goog-drz-eventarc-uuid     = "4830dd8d-2c3b-4321-ae8d-958fa1a2c3ab"
    goog-eventarc              = ""
    goog-drz-eventarc-location = "us-west1"
  }

  message_retention_duration = "86400s"
  name                       = "eventarc-us-west1-data-collection-bay-area-511-event-073018-sub-940"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      audience              = "https://data-collection-bay-area-511-event-et73rt2k6a-uw.a.run.app"
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://data-collection-bay-area-511-event-et73rt2k6a-uw.a.run.app?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fcloud-city-cal%2Ftopics%2Fscheduler.BayArea511DataCollectionScheduledEvent"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/scheduler.BayArea511DataCollectionScheduledEvent"
}
# terraform import google_pubsub_subscription.eventarc_us_west1_data_collection_bay_area_511_event_073018_sub_940 projects/cloud-city-cal/subscriptions/eventarc-us-west1-data-collection-bay-area-511-event-073018-sub-940
