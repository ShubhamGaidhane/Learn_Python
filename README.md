# API to GCS NDJSON Loader

This script fetches raw, unflattened data from a JSON API, sanitizes all field names to be BigQuery-compatible, converts the data to newline-delimited JSON (NDJSON), and uploads it to a Google Cloud Storage (GCS) bucket.

## Features

- **Intelligent Data Handling:** The script automatically detects and handles different API response structures:
    - **List of Objects:** If the response is a list, each object is treated as a separate record.
    - **Dictionary of Records (e.g., `apis.guru`):** If the response is a dictionary where all values are also dictionaries, the script treats it as a dictionary of records. For each key-value pair, it creates a new JSON object of the form `{ "key": { ...value } }`, which becomes a single record in the NDJSON file.
    - **Single Record Object (e.g., DigitalOcean status):** If the response is a dictionary that doesn't match the "dictionary of records" structure, the entire object is treated as a single record.
- **BigQuery-Compatible Keys:** Recursively sanitizes all keys in the JSON data to ensure they are valid for BigQuery. The sanitization process includes:
    - Converting all keys to lowercase.
    - Replacing invalid characters with underscores.
    - Prefixing keys that start with a number with an underscore.
    - Appending a numeric suffix to any duplicate keys that result from this process.
- Converts the sanitized data to NDJSON format.
- Uploads the NDJSON file to a GCS bucket with the correct `content_type` (`application/x-ndjson`).

## Prerequisites

- Python 3.6+
- Google Cloud SDK authenticated with your GCP account.
- The following Python libraries installed:
  - `google-cloud-storage`
  - `requests`

You can install the required libraries using pip:
```bash
pip install google-cloud-storage requests
```

## Usage

The script is executed from the command line with the following arguments:

- `--api_url`: The URL of the API endpoint to fetch data from. (Required)
- `--bucket_name`: The name of the GCS bucket to upload the file to. (Required)
- `--blob_name`: The desired name for the file in the GCS bucket. (Required)

### Example 1: API returning a single record object

```powershell
python ./api_to_gcs_ndjson_unflattened.py `
    --api_url "https://status.digitalocean.com/api/v2/summary.json" `
    --bucket_name "your-gcs-bucket-name" `
    --blob_name "digitalocean_status.ndjson"
```
This will produce a single-line NDJSON file containing the entire object.

### Example 2: API returning a dictionary of records

```powershell
python ./api_to_gcs_ndjson_unflattened.py `
    --api_url "https://api.apis.guru/v2/list.json" `
    --bucket_name "your-gcs-bucket-name" `
    --blob_name "apis_guru_list.ndjson"
```
This will produce a multi-line NDJSON file. Each line will be a JSON object where the top-level key is the API name (e.g., `"1forge.com"`) and the value is the corresponding API data.
