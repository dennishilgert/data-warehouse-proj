# Project for the data warehouse lecture

This project includes the deployment of MinIO in a Kubernetes cluster as well as collecting public weather data from OpenWeatherMap and saving it in the Parquet format in MinIO.

To deploy MinIO in the kubernetes cluster, run the `deployment/deploy.sh` script. This will not only deploy MinIO in the cluster, it will also forward all necessary ports to use MinIO from outside of the cluster.

The data-collection can be startet with the command `python3 fetch_and_store.py`. The script will collect the weather data for defined cities in a specific interval.