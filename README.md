# Project for the data warehouse lecture

This project includes the deployment of MinIO in a Kubernetes cluster as well as collecting public weather data from OpenWeatherMap and saving it in the Parquet format in MinIO.

Important: Please rename or duplicate the file `.env.sample` to `.env` and change the API_KEY in the `.env` file to the one provided.

To deploy MinIO in the Kubernetes cluster, run the `deployment/deploy.sh` script. Please make sure you navigate into the `deployment` directory before you execute the deploy script.
Running the script will not only deploy MinIO in the cluster, it will also forward all necessary ports to use MinIO from outside of the cluster.

To access the Kubernetes dashboard, use [this url](http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/).
The access token can be generated with this `kubectl get secret admin-user -n kubernetes-dashboard -o jsonpath={".data.token"} | base64 -d` command.

After MinIO has been deployed to the Kubernetes cluster, the data-collection can be startet with the command `python3 fetch_and_store.py`. The script will collect the weather data for the defined cities in a specific interval.