resource "google_pubsub_topic" "data_pems" {
  name    = "data.pems"
  project = "cloud-city-cal"

  schema_settings {
    encoding = "BINARY"
    schema   = "projects/cloud-city-cal/schemas/data.pems"
  }
}
# terraform import google_pubsub_topic.data_pems projects/cloud-city-cal/topics/data.pems
