resource "google_bigquery_table" "pems_partitioned" {
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

  schema   = "[{\"mode\":\"NULLABLE\",\"name\":\"time\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"station_id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"district\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"freeway\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"direction\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"lane_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"station_length\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"samples\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"percentage_observed\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"total_flow\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"average_occupancy\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"average_speed\",\"type\":\"FLOAT\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"samples\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"flow\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"average_occupancy\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"average_speed\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"observed\",\"type\":\"BOOLEAN\"}],\"mode\":\"REPEATED\",\"name\":\"lanes\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"subscription_name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"message_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"publish_time\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"attributes\",\"type\":\"JSON\"}]"
  table_id = "pems_partitioned"
}
# terraform import google_bigquery_table.pems_partitioned projects/cloud-city-cal/datasets/cloud_city/tables/pems_partitioned
