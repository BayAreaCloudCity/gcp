resource "google_pubsub_topic" "scheduler_bayarea511datacollectionscheduledevent" {
  name    = "scheduler.BayArea511DataCollectionScheduledEvent"
  project = "cloud-city-cal"
}
# terraform import google_pubsub_topic.scheduler_bayarea511datacollectionscheduledevent projects/cloud-city-cal/topics/scheduler.BayArea511DataCollectionScheduledEvent
