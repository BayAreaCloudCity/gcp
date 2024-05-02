resource "google_pubsub_topic" "scheduler_weatherdatacollectionscheduledevent" {
  name    = "scheduler.WeatherDataCollectionScheduledEvent"
  project = "cloud-city-cal"
}
# terraform import google_pubsub_topic.scheduler_weatherdatacollectionscheduledevent projects/cloud-city-cal/topics/scheduler.WeatherDataCollectionScheduledEvent
