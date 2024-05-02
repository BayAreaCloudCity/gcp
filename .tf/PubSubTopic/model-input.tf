resource "google_pubsub_topic" "model_input" {
  name    = "model.input"
  project = "cloud-city-cal"

  schema_settings {
    encoding = "BINARY"
    schema   = "projects/cloud-city-cal/schemas/model.input"
  }
}
# terraform import google_pubsub_topic.model_input projects/cloud-city-cal/topics/model.input
