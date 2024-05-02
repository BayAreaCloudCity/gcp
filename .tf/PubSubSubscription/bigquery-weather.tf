resource "google_pubsub_subscription" "bigquery_weather" {
  ack_deadline_seconds = 10

  bigquery_config {
    table            = "cloud-city-cal.cloud_city.weather_partitioned"
    use_topic_schema = true
    write_metadata   = true
  }

  message_retention_duration = "604800s"
  name                       = "bigquery.weather"
  project                    = "cloud-city-cal"
  topic                      = "projects/cloud-city-cal/topics/data.weather"
}
# terraform import google_pubsub_subscription.bigquery_weather projects/cloud-city-cal/subscriptions/bigquery.weather
