
import argparse
import json
import re
import requests
from google.cloud import storage

def sanitize_key(key):
    """Sanitizes a string to be a valid BigQuery column name."""
    key_str = str(key)
    # Convert to lowercase to handle case-insensitivity
    sanitized = key_str.lower()
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-z0-9_]', '_', sanitized)
    # Add a prefix if the key starts with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    # Truncate to 300 characters, BigQuery's limit
    return sanitized[:300]

def sanitize_data_keys(data):
    """
    Recursively sanitizes all keys in a JSON object (dicts and lists),
    handling case-insensitive duplicates.
    """
    if isinstance(data, dict):
        new_dict = {}
        seen_keys = set()
        for k, v in data.items():
            sanitized_k = sanitize_key(k)
            original_sanitized_k = sanitized_k
            suffix = 1
            # Handle potential collisions from sanitization (e.g., 'V2' and 'v2')
            while sanitized_k in seen_keys:
                sanitized_k = f"{original_sanitized_k}_{suffix}"
                suffix += 1

            seen_keys.add(sanitized_k)
            new_dict[sanitized_k] = sanitize_data_keys(v)
        return new_dict
    elif isinstance(data, list):
        return [sanitize_data_keys(item) for item in data]
    else:
        return data

def fetch_data_from_api(api_url):
    """Fetches data from the specified API endpoint."""
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def convert_to_ndjson(data):
    """Converts a list of JSON objects to a newline-delimited JSON string."""
    if not data:
        return ""

    ndjson_lines = [json.dumps(item) for item in data]
    return "\n".join(ndjson_lines) + "\n"

def upload_to_gcs(bucket_name, destination_blob_name, data):
    """Uploads data to a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data, content_type='application/x-ndjson')
    print(f"Data uploaded to gs://{bucket_name}/{destination_blob_name}")

def main():
    """Main function to fetch, convert, and upload data."""
    parser = argparse.ArgumentParser(description="Fetch raw API data, sanitize keys, and upload to GCS in NDJSON format.")
    parser.add_argument("--api_url", required=True, help="The API endpoint URL.")
    parser.add_argument("--bucket_name", required=True, help="The GCS bucket name.")
    parser.add_argument("--blob_name", required=True, help="The destination blob name in GCS.")
    args = parser.parse_args()

    # Fetch data
    api_data = fetch_data_from_api(args.api_url)

    records = []
    if isinstance(api_data, dict):
        # Heuristic to identify a "dictionary of records" like apis.guru
        is_dict_of_records = api_data and all(isinstance(v, dict) for v in api_data.values())

        if is_dict_of_records:
            # For this structure, each key-value pair is a record.
            for key, value in api_data.items():
                records.append({key: value})
        else:
            # Otherwise, the entire object is a single record.
            records = [api_data]
    elif isinstance(api_data, list):
        records = api_data
    else:
        print(f"Warning: API returned an unexpected data type: {type(api_data)}. Treating as empty list.")
        records = []

    # Sanitize all records before converting to NDJSON
    sanitized_records = [sanitize_data_keys(record) for record in records]

    # Convert to NDJSON
    ndjson_data = convert_to_ndjson(sanitized_records)

    # Upload to GCS
    upload_to_gcs(args.bucket_name, args.blob_name, ndjson_data)

if __name__ == "__main__":
    main()
