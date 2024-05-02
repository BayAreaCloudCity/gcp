resource "google_pubsub_subscription" "eventarc_us_west1_cf_preprocess_753210_sub_502" {
  ack_deadline_seconds = 600

  labels = {
    goog-eventarc              = ""
    goog-drz-eventarc-location = "us-west1"
    goog-drz-eventarc-uuid     = "1e2d88b2-662b-4f8d-bf0b-22d34e4ad676"
  }

  message_retention_duration = "86400s"
  name                       = "eventarc-us-west1-cf-preprocess-753210-sub-502"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      audience              = "https://cf-preprocess-et73rt2k6a-uw.a.run.app"
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://cf-preprocess-et73rt2k6a-uw.a.run.app?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fcloud-city-cal%2Ftopics%2Fscheduler.PreprocessingTriggerEvent"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/scheduler.PreprocessingTriggerEvent"
}
# terraform import google_pubsub_subscription.eventarc_us_west1_cf_preprocess_753210_sub_502 projects/cloud-city-cal/subscriptions/eventarc-us-west1-cf-preprocess-753210-sub-502
