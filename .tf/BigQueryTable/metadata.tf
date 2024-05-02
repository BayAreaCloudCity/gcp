resource "google_bigquery_table" "metadata" {
  dataset_id = "cloud_city"
  project    = "cloud-city-cal"
  schema     = "[{\"mode\":\"NULLABLE\",\"name\":\"version\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"data\",\"type\":\"JSON\"}]"
  table_id   = "metadata"
}
# terraform import google_bigquery_table.metadata projects/cloud-city-cal/datasets/cloud_city/tables/metadata
