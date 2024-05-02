resource "google_pubsub_topic" "replayer_triggeredevent" {
  name    = "replayer.TriggeredEvent"
  project = "cloud-city-cal"
}
# terraform import google_pubsub_topic.replayer_triggeredevent projects/cloud-city-cal/topics/replayer.TriggeredEvent
