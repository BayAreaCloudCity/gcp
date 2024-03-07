# Cloud City *on Google Cloud Platform*

This project is a demo of using Google Cloud Platform to build a smart city application. We built a traffic model for Bay Area
using straightforward machine learning modeling techniques to demostrate this. 

This README only contains instructions on how to deploy this file system. 
Please refer to our project report (*coming soon*) to learn more about our design.


## Data Ingestion

We ingest data from a variety of sources, including [PeMS](https://pems.dot.ca.gov/), [OpenWeatherAPI](https://openweathermap.org/api), and [511.org](https://511.org).
Data are ingested on real-time or a daily basis, using Google Cloud Scheduler and Cloud Function. 