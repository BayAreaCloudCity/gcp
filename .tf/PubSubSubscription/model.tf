resource "google_pubsub_subscription" "model" {
  ack_deadline_seconds = 10

  expiration_policy {
    ttl = "2678400s"
  }

  message_retention_duration = "604800s"
  name                       = "model"
  project                    = "cloud-city-cal"

  push_config {
    oidc_token {
      service_account_email = "163650808003-compute@developer.gserviceaccount.com"
    }

    push_endpoint = "https://us-west1-cloud-city-cal.cloudfunctions.net/model"
  }

  retry_policy {
    maximum_backoff = "600s"
    minimum_backoff = "10s"
  }

  topic = "projects/cloud-city-cal/topics/model.input"
}
# terraform import google_pubsub_subscription.model projects/cloud-city-cal/subscriptions/model
