# Google ADK Agent for Cloud Function Trigger

This project contains a Google ADK agent that triggers a Cloud Function to load data from a public API endpoint to a specific Google Cloud Storage (GCS) location.

This guide is tailored for the following setup:
- **Google Cloud Project ID:** `adk-test-476608`
- **Region:** `us-central1`

## Project Structure

```
.
├── adk_agent
│   └── gcs_loader_agent
│       ├── .env
│       ├── __init__.py
│       └── agent.py
└── cloud_function
    ├── main.py
    └── requirements.txt
```

## Cloud Function Setup

### `cloud_function/main.py`

This function is triggered via HTTP, takes a JSON payload with an `api_url` and a `gcs_uri`, fetches the data, and uploads it to the specified GCS location.

```python
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
```

### `cloud_function/requirements.txt`

```
functions-framework==3.*
requests
google-cloud-storage
```

### Deployment Instructions

1.  **Authenticate with gcloud:**
    ```bash
    gcloud auth login
    ```
2.  **Set your project:**
    ```bash
    gcloud config set project adk-test-476608
    ```
3.  **Deploy the function:**
    ```bash
    gcloud functions deploy load_data_from_api \
      --runtime python311 \
      --trigger-http \
      --allow-unauthenticated \
      --source ./cloud_function \
      --entry-point load_data_from_api \
      --region us-central1
    ```
4.  **Get the trigger URL:** After deployment, the command will output a trigger URL. Copy this URL.

## ADK Agent Setup

### `adk_agent/gcs_loader_agent/.env`

Create a `.env` file inside `adk_agent/gcs_loader_agent/` and add the following content. Replace `[YOUR_CLOUD_FUNCTION_TRIGGER_URL]` with the URL you copied from the deployment step.

```
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=adk-test-476608
GOOGLE_CLOUD_LOCATION=us-central1
CLOUD_FUNCTION_URL=[YOUR_CLOUD_FUNCTION_TRIGGER_URL]
```

### `adk_agent/gcs_loader_agent/agent.py`

This agent is configured with a tool that knows how to call the Cloud Function you just deployed.

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import requests
import os
import re

def trigger_cloud_function(api_url: str, gcs_uri: str):
    """
    Triggers a Cloud Function to load data from an API to a GCS bucket.

    Args:
        api_url: The URL of the API to fetch data from.
        gcs_uri: The GCS URI of the destination object (e.g., "gs://bucket-name/path/to/file.json").
    """
    # Validate GCS URI format
    if not re.match(r"gs://([^/]+)/(.+)", gcs_uri):
        return f"Invalid GCS URI format: {gcs_uri}. Please use the format 'gs://bucket-name/path/to/file.json'."

    cloud_function_url = os.environ.get("CLOUD_FUNCTION_URL")
    if not cloud_function_url or cloud_function_url == "YOUR_CLOUD_FUNCTION_URL":
        return "Cloud Function URL is not configured. Please set the CLOUD_FUNCTION_URL environment variable."

    payload = {
        "api_url": api_url,
        "gcs_uri": gcs_uri
    }

    try:
        response = requests.post(cloud_function_url, json=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error triggering Cloud Function: {e}"

root_agent = Agent(
    model='gemini-1.5-flash',
    name='gcs_loader_agent',
    description='An agent that can trigger a Cloud Function to load data from an API to a specific GCS URI.',
    instruction='Use the trigger_cloud_function tool to load data from a public API to a given GCS URI. You must be provided with both the API URL and the full GCS URI (e.g., gs://my-bucket/data/output.json).',
    tools=[FunctionTool(trigger_cloud_function)]
)
```

## Running the Agent

1.  **Install dependencies:**
    ```bash
    pip install google-adk
    ```
2.  **Run the agent:**
    ```bash
    adk run adk_agent/gcs_loader_agent
    ```
3.  **Interact with the agent:**
    You can now ask the agent to load the data using the API and GCS URI you provided.

    **Example:**
    `[user]: Please load data from the API at https://jsonplaceholder.typicode.com/posts to the GCS location gs://adk-artifact-files/API_Data/posts_1.json`

The agent will trigger the Cloud Function, which will fetch the data and save it to your specified GCS path.
