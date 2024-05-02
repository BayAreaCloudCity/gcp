resource "google_bigquery_table" "weather_partitioned" {
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

  schema   = "[{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"lon\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"lat\",\"type\":\"FLOAT\"}],\"mode\":\"NULLABLE\",\"name\":\"coord\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"main\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"description\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"icon\",\"type\":\"STRING\"}],\"mode\":\"REPEATED\",\"name\":\"weather\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"base\",\"type\":\"STRING\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"temp\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"feels_like\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"temp_min\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"temp_max\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"pressure\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"humidity\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"sea_level_pressure\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"ground_level_pressure\",\"type\":\"INTEGER\"}],\"mode\":\"NULLABLE\",\"name\":\"main\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"visibility\",\"type\":\"INTEGER\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"speed\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"deg\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"gust\",\"type\":\"FLOAT\"}],\"mode\":\"NULLABLE\",\"name\":\"wind\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"last_1h\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"last_3h\",\"type\":\"FLOAT\"}],\"mode\":\"NULLABLE\",\"name\":\"rain\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"last_1h\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"last_3h\",\"type\":\"FLOAT\"}],\"mode\":\"NULLABLE\",\"name\":\"snow\",\"type\":\"RECORD\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"all\",\"type\":\"INTEGER\"}],\"mode\":\"NULLABLE\",\"name\":\"clouds\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"dt\",\"type\":\"INTEGER\"},{\"fields\":[{\"mode\":\"NULLABLE\",\"name\":\"type\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"country\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"sunrise\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"sunset\",\"type\":\"INTEGER\"}],\"mode\":\"NULLABLE\",\"name\":\"sys\",\"type\":\"RECORD\"},{\"mode\":\"NULLABLE\",\"name\":\"timezone\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"id\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"cod\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"subscription_name\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"message_id\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"publish_time\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"attributes\",\"type\":\"JSON\"}]"
  table_id = "weather_partitioned"
}
# terraform import google_bigquery_table.weather_partitioned projects/cloud-city-cal/datasets/cloud_city/tables/weather_partitioned
