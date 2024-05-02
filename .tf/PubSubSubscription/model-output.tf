resource "google_pubsub_subscription" "model_output" {
  ack_deadline_seconds = 10

  bigquery_config {
    table            = "cloud-city-cal.cloud_city.output_partitioned"
    use_topic_schema = true
    write_metadata   = true
  }

  expiration_policy {
    ttl = "2678400s"
  }

  message_retention_duration = "604800s"
  name                       = "model.output"
  project                    = "cloud-city-cal"
  topic                      = "projects/cloud-city-cal/topics/model.output"
}
# terraform import google_pubsub_subscription.model_output projects/cloud-city-cal/subscriptions/model.output
