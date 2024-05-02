resource "google_bigquery_table" "processed_partitioned" {
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

  schema   = "[{\"mode\":\"REPEATED\",\"name\":\"coefficients\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"metadata_version\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"timestamp\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"segment_id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"subscription_name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"message_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"publish_time\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"attributes\",\"type\":\"JSON\"}]"
  table_id = "processed_partitioned"
}
# terraform import google_bigquery_table.processed_partitioned projects/cloud-city-cal/datasets/cloud_city/tables/processed_partitioned
