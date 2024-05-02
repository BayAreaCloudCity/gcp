resource "google_pubsub_topic" "data_bay_area_511_event" {
  name    = "data.bay_area_511_event"
  project = "cloud-city-cal"

  schema_settings {
    encoding = "BINARY"
    schema   = "projects/cloud-city-cal/schemas/data.bay-area-511-event"
  }
}
# terraform import google_pubsub_topic.data_bay_area_511_event projects/cloud-city-cal/topics/data.bay_area_511_event
