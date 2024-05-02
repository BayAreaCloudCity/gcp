resource "google_pubsub_topic" "data_weather" {
  name    = "data.weather"
  project = "cloud-city-cal"

  schema_settings {
    encoding = "BINARY"
    schema   = "projects/cloud-city-cal/schemas/data.weather"
  }
}
# terraform import google_pubsub_topic.data_weather projects/cloud-city-cal/topics/data.weather
