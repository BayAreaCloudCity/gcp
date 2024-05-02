resource "google_pubsub_subscription" "eventarc_us_west1_replayer_708717_sub_242" {
  ack_deadline_seconds = 600

  labels = {
    goog-drz-eventarc-location = "us-west1"
    goog-drz-eventarc-uuid     = "e059a6e3-0e8b-4ac9-96df-ffd891e06fec"
    goog-eventarc              = ""
  }

  message_retention_duration = "86400s"
  name                       = "eventarc-us-west1-replayer-708717-sub-242"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      audience              = "https://replayer-et73rt2k6a-uw.a.run.app"
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://replayer-et73rt2k6a-uw.a.run.app?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fcloud-city-cal%2Ftopics%2Freplayer.TriggeredEvent"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/replayer.TriggeredEvent"
}
# terraform import google_pubsub_subscription.eventarc_us_west1_replayer_708717_sub_242 projects/cloud-city-cal/subscriptions/eventarc-us-west1-replayer-708717-sub-242
