"""
This script fetches weather data from the OpenWeatherMap API for a list of cities,
converts the data into a structured format using pandas DataFrames, and uploads the
aggregated data to a MinIO bucket in Parquet format.
"""

import time
import requests
import boto3
from io import BytesIO
import pandas as pd
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Configuration for OpenWeatherMap API and MinIO storage
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_BASE_URL')
cities = os.getenv('CITIES').split(',')

minio_endpoint = os.getenv('MINIO_ENDPOINT')
minio_root_user = os.getenv('MINIO_ROOT_USER')
minio_root_password = os.getenv('MINIO_ROOT_PASSWORD')
bucket_name = os.getenv('MINIO_BUCKET_NAME')

def current_milli_time():
    """
    Get the current time in milliseconds.

    Returns:
        int: Current time in milliseconds.
    """
    return round(time.time() * 1000)



def fetch_weather_data(url):
    """
    Fetch weather data from the specified URL.

    Args:
        url (str): URL to fetch the weather data from.

    Returns:
        dict: Weather data as a JSON dictionary.
    
    Raises:
        HTTPError: If the response contains an unsuccessful status code.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()



def data_to_dataframe(data, all_data_df=None):
    """
    Convert weather data into a pandas DataFrame.

    Args:
        data (dict): Single city weather data to be converted.
        all_data_df (pd.DataFrame, optional): DataFrame to append the data to. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame containing the weather data.
    """
    weather_data = {
        'city': data['name'],
        'temperature': data['main']['temp'],
        'feels_like': data['main']['feels_like'],
        'description': data['weather'][0]['description'],
        'pressure': data['main']['pressure'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'sunrise': data['sys']['sunrise'],
        'sunset': data['sys']['sunset'],
        'timestamp': current_milli_time()
    }
    new_df = pd.DataFrame([weather_data])
    return pd.concat([all_data_df, new_df], ignore_index=True) if all_data_df is not None else new_df



def upload_to_minio(dataframe, client, bucket_name, object_name):
    """
    Upload a DataFrame to MinIO in Parquet format.

    Args:
        dataframe (pd.DataFrame): DataFrame to upload.
        client: MinIO client object.
        bucket_name (str): Name of the MinIO bucket.
        object_name (str): Name for the object to be saved as in the bucket.

    Prints:
        Success or error message indicating the upload status.
    """
    parquet_buffer = BytesIO()
    dataframe.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)
    
    try:
        client.put_object(Bucket=bucket_name, Key=object_name, Body=parquet_buffer.getvalue())
        print(f'{object_name} uploaded to MinIO successfully')
    except NoCredentialsError:
        print('Invalid MinIO credentials')



def check_and_create_bucket(client, bucket_name):
    """
    Check if a MinIO bucket exists and create it if it does not.

    Args:
        client: MinIO client object.
        bucket_name (str): Name of the bucket to check and possibly create.

    Prints:
        Status of bucket creation or existence.
    """
    try:
        existing_buckets = [bucket['Name'] for bucket in client.list_buckets()['Buckets']]
        if bucket_name not in existing_buckets:
            client.create_bucket(Bucket=bucket_name)
            print(f'Bucket "{bucket_name}" created successfully.')
        else:
            print(f'Bucket "{bucket_name}" already exists.')
    except Exception as e:
        print(f'Error checking or creating bucket: {e}')



def main():
    """
    Main function to orchestrate fetching weather data, processing it, and uploading to MinIO.
    """
    s3_client = boto3.client('s3',
                             endpoint_url=f'http://{minio_endpoint}',
                             aws_access_key_id=minio_root_user,
                             aws_secret_access_key=minio_root_password,
                             region_name='eu-west-1',
                             config=boto3.session.Config(signature_version='s3v4'))
    
    # Ensure bucket exists
    check_and_create_bucket(s3_client, bucket_name)

    count = 10
    i = 1
    while i < count + 1:
        all_weather_data = None
        for city in cities:
            print(f'fetching weather for {city}')
            weather_data = fetch_weather_data(f'{base_url}?q={city}&appid={api_key}&units=metric')
            all_weather_data = data_to_dataframe(weather_data, all_weather_data)
        
        if all_weather_data is not None:
            print(all_weather_data)
            file_name = f'weather-data-aggregated-{current_milli_time()}.parquet'
            upload_to_minio(all_weather_data, s3_client, bucket_name, file_name)
        
        i += 1
        time.sleep(5)



if __name__ == '__main__':
    main()
