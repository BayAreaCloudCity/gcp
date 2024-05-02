resource "google_pubsub_subscription" "bigquery_bay_area_511_event" {
  ack_deadline_seconds = 10

  bigquery_config {
    table            = "cloud-city-cal.cloud_city.bay_area_511_event_partitioned"
    use_topic_schema = true
    write_metadata   = true
  }

  expiration_policy {
    ttl = "2678400s"
  }

  message_retention_duration = "604800s"
  name                       = "bigquery.bay_area_511_event"
  project                    = "cloud-city-cal"
  topic                      = "projects/cloud-city-cal/topics/data.bay_area_511_event"
}
# terraform import google_pubsub_subscription.bigquery_bay_area_511_event projects/cloud-city-cal/subscriptions/bigquery.bay_area_511_event
