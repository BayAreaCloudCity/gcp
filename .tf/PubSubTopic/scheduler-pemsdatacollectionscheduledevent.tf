resource "google_pubsub_topic" "scheduler_pemsdatacollectionscheduledevent" {
  name    = "scheduler.PeMSDataCollectionScheduledEvent"
  project = "cloud-city-cal"
}
# terraform import google_pubsub_topic.scheduler_pemsdatacollectionscheduledevent projects/cloud-city-cal/topics/scheduler.PeMSDataCollectionScheduledEvent
