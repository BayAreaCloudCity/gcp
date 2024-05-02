resource "google_bigquery_table" "bay_area_511_event_partitioned" {
  dataset_id = "cloud_city"
  project    = "cloud-city-cal"

  range_partitioning {
    field = "publish_time"

    range {
      end      = 1735632000000000
      interval = 86400000000
      start    = 1672560000000000
    }
  }

  schema   = "[{\"mode\":\"NULLABLE\",\"name\":\"url\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"jurisdiction_url\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"status\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"headline\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"event_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"severity\",\"type\":\"STRING\"},{\"fields\":[{\"mode\":\"REPEATED\",\"name\":\"coordinates\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"type\",\"type\":\"STRING\"}],\"mode\":\"NULLABLE\",\"name\":\"geography_point\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"REPEATED\",\"name\":\"coordinates\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"type\",\"type\":\"STRING\"}],\"mode\":\"NULLABLE\",\"name\":\"closure_geometry_point\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"created\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"updated\",\"type\":\"STRING\"},{\"fields\":[{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"start_date\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"end_date\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"daily_start_time\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"daily_end_time\",\"type\":\"STRING\"},{\"mode\":\"REPEATED\",\"name\":\"days\",\"type\":\"STRING\"}],\"mode\":\"REPEATED\",\"name\":\"recurring_schedules\",\"type\":\"RECORD\"},{\"mode\":\"REPEATED\",\"name\":\"exceptions\",\"type\":\"STRING\"},{\"mode\":\"REPEATED\",\"name\":\"intervals\",\"type\":\"STRING\"}],\"mode\":\"NULLABLE\",\"name\":\"schedule\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"timezone\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"description\",\"type\":\"STRING\"},{\"mode\":\"REPEATED\",\"name\":\"event_subtypes\",\"type\":\"STRING\"},{\"mode\":\"REPEATED\",\"name\":\"grouped_events\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"detour\",\"type\":\"STRING\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"from\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"to\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"state\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"direction\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"impacted_lane_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"road_advisory\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"lane_status\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"article\",\"type\":\"STRING\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"url\",\"type\":\"STRING\"}],\"mode\":\"REPEATED\",\"name\":\"areas\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"lanes_open\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"lanes_closed\",\"type\":\"INTEGER\"},{\"mode\":\"REPEATED\",\"name\":\"impacted_systems\",\"type\":\"STRING\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"restriction_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"value\",\"type\":\"FLOAT\"}],\"mode\":\"REPEATED\",\"name\":\"restrictions\",\"type\":\"RECORD\"}],\"mode\":\"REPEATED\",\"name\":\"roads\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"url\",\"type\":\"STRING\"}],\"mode\":\"REPEATED\",\"name\":\"areas\",\"type\":\"RECORD\"},{\"mode\":\"REPEATED\",\"name\":\"attachments\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"source_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"source_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"subscription_name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"message_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"publish_time\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"attributes\",\"type\":\"JSON\"}]"
  table_id = "bay_area_511_event_partitioned"
}
# terraform import google_bigquery_table.bay_area_511_event_partitioned projects/cloud-city-cal/datasets/cloud_city/tables/bay_area_511_event_partitioned