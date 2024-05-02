resource "google_bigquery_table" "output_partitioned" {
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

  schema   = "[{\"mode\":\"NULLABLE\",\"name\":\"output\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"metadata_version\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"timestamp\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"segment_id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"subscription_name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"message_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"publish_time\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"attributes\",\"type\":\"JSON\"}]"
  table_id = "output_partitioned"
}
# terraform import google_bigquery_table.output_partitioned projects/cloud-city-cal/datasets/cloud_city/tables/output_partitioned
