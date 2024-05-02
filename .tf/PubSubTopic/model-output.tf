resource "google_pubsub_topic" "model_output" {
  name    = "model.output"
  project = "cloud-city-cal"

  schema_settings {
    encoding = "BINARY"
    schema   = "projects/cloud-city-cal/schemas/model.output"
  }
}
# terraform import google_pubsub_topic.model_output projects/cloud-city-cal/topics/model.output
