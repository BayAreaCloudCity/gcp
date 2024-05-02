resource "google_pubsub_topic" "scheduler_preprocessingtriggerevent" {
  name    = "scheduler.PreprocessingTriggerEvent"
  project = "cloud-city-cal"
}
# terraform import google_pubsub_topic.scheduler_preprocessingtriggerevent projects/cloud-city-cal/topics/scheduler.PreprocessingTriggerEvent
