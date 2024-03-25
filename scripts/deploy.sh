#!/bin/bash

set -e

# Array for the pids of the background processes
declare -a pids

# Function to kill a background processes
cleanup() {
    echo "Killing all background processes ..."
    for pid in "${pids[@]}"; do
        echo "Killing $pid"
        if kill -0 $pid 2>/dev/null; then
            kill $pid
        fi
    done
    exit 0
}

# Trap, to react to SIGINT (Ctrl+C)
trap cleanup SIGINT

# Apply minio manifest
kubectl apply -f ../deployment/minio.yaml

# Proxying kubernetes dashboard
kubectl proxy >/dev/null 2>&1 &
pids+=($!)
echo "Proxying kubernetes dashboard in background-process $!"

# Starting port forwardings for the minio deployment
kubectl port-forward service/minio 9090:9090 -n minio-ns >/dev/null 2>&1 &
pids+=($!)
echo "Forwarding port 9090 in background-process $!"

kubectl port-forward service/minio 9000:9000 -n minio-ns >/dev/null 2>&1 &
pids+=($!)
echo "Forwarding port 9000 in background-process $!"

# Blocking until the process is cancelled
echo "Port forwardings are running. Press Ctrl+C to exit."
while true; do
    sleep 1
done
