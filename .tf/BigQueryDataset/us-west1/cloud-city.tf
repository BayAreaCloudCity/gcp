resource "google_bigquery_dataset" "cloud_city" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                 = "cloud_city"
  delete_contents_on_destroy = false
  location                   = "us-west1"
  project                    = "cloud-city-cal"
}
# terraform import google_bigquery_dataset.cloud_city projects/cloud-city-cal/datasets/cloud_city
