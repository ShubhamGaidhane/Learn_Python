import functions_framework
import requests
from google.cloud import storage
import os
import re

@functions_framework.http
def load_data_from_api(request):
    """
    HTTP Cloud Function to fetch data from an API and upload it to a GCS bucket.
    Expects a JSON payload with 'api_url' and 'gcs_uri'.
    """
    request_json = request.get_json(silent=True)

    if not request_json or 'api_url' not in request_json or 'gcs_uri' not in request_json:
        return 'Invalid request: JSON payload must contain "api_url" and "gcs_uri".', 400

    api_url = request_json['api_url']
    gcs_uri = request_json['gcs_uri']

    # Parse GCS URI
    match = re.match(r"gs://([^/]+)/(.+)", gcs_uri)
    if not match:
        return f"Invalid GCS URI format: {gcs_uri}", 400

    bucket_name = match.group(1)
    file_path = match.group(2)

    try:
        # Fetch data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Upload data to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        blob.upload_from_string(response.content, content_type=response.headers.get('Content-Type', 'application/json'))

        return f"Successfully fetched data from {api_url} and uploaded to {gcs_uri}", 200

    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {e}", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500
