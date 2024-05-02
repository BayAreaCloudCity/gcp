resource "google_pubsub_subscription" "eventarc_us_west1_data_collection_weather_2_003578_sub_617" {
  ack_deadline_seconds = 600

  labels = {
    goog-drz-eventarc-location = "us-west1"
    goog-drz-eventarc-uuid     = "6c3db25f-d02c-48e5-bf9c-fc75d3a44c5b"
    goog-eventarc              = ""
  }

  message_retention_duration = "86400s"
  name                       = "eventarc-us-west1-data-collection-weather-2-003578-sub-617"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      audience              = "https://data-collection-weather-2-et73rt2k6a-uw.a.run.app"
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://data-collection-weather-2-et73rt2k6a-uw.a.run.app?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fcloud-city-cal%2Ftopics%2Fscheduler.WeatherDataCollectionScheduledEvent"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/scheduler.WeatherDataCollectionScheduledEvent"
}
# terraform import google_pubsub_subscription.eventarc_us_west1_data_collection_weather_2_003578_sub_617 projects/cloud-city-cal/subscriptions/eventarc-us-west1-data-collection-weather-2-003578-sub-617
