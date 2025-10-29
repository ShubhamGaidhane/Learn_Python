import functions_framework
import requests
from google.cloud import storage
import os

@functions_framework.http
def load_data_from_api(request):
    """
    HTTP Cloud Function to fetch data from an API and upload it to a GCS bucket.
    Expects a JSON payload with 'api_url' and 'bucket_name'.
    """
    request_json = request.get_json(silent=True)

    if not request_json or 'api_url' not in request_json or 'bucket_name' not in request_json:
        return 'Invalid request: JSON payload must contain "api_url" and "bucket_name".', 400

    api_url = request_json['api_url']
    bucket_name = request_json['bucket_name']

    # Extract a filename from the URL, or use a default
    file_name = api_url.split('/')[-1]
    if not file_name:
        file_name = "api_data.json"

    try:
        # Fetch data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Upload data to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        blob.upload_from_string(response.content, content_type=response.headers.get('Content-Type', 'application/octet-stream'))

        return f"Successfully fetched data from {api_url} and uploaded to gs://{bucket_name}/{file_name}", 200

    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {e}", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500
