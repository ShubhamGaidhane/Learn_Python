# Google ADK Agent for Cloud Function Trigger

This project contains a Google ADK agent that triggers a Cloud Function to load data from an API endpoint to a GCS bucket.

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

```python
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
    gcloud config set project [YOUR_PROJECT_ID]
    ```
3.  **Deploy the function:**
    ```bash
    gcloud functions deploy load_data_from_api \
      --runtime python311 \
      --trigger-http \
      --allow-unauthenticated \
      --source ./cloud_function \
      --entry-point load_data_from_api \
      --region [YOUR_REGION]
    ```
    Replace `[YOUR_PROJECT_ID]` and `[YOUR_REGION]` with your actual project ID and desired region.

4.  **Get the trigger URL:** After deployment, the command will output a trigger URL. You will need this for the ADK agent.

## ADK Agent Setup

### `adk_agent/gcs_loader_agent/__init__.py`

```python
from . import agent
```

### `adk_agent/gcs_loader_agent/.env`

```
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=[YOUR_PROJECT_ID]
GOOGLE_CLOUD_LOCATION=[YOUR_REGION]
CLOUD_FUNCTION_URL=[YOUR_CLOUD_FUNCTION_TRIGGER_URL]
```
Replace the placeholders with your project ID, region, and the Cloud Function trigger URL from the previous step.

### `adk_agent/gcs_loader_agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import requests
import os

def trigger_cloud_function(api_url: str, bucket_name: str):
    """
    Triggers a Cloud Function to load data from an API to a GCS bucket.

    Args:
        api_url: The URL of the API to fetch data from.
        bucket_name: The name of the GCS bucket to upload the data to.
    """
    cloud_function_url = os.environ.get("CLOUD_FUNCTION_URL", "YOUR_CLOUD_FUNCTION_URL")

    if cloud_function_url == "YOUR_CLOUD_FUNCTION_URL":
        return "Cloud Function URL is not configured."

    payload = {
        "api_url": api_url,
        "bucket_name": bucket_name
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
    description='An agent that can trigger a Cloud Function to load data from an API to a GCS bucket.',
    instruction='Use the trigger_cloud_function tool to load data from an API to a GCS bucket.',
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
    You can now ask the agent to load data. For example:

    `[user]: Load data from https://api.publicapis.org/entries to my-gcs-bucket`

The agent will then trigger the Cloud Function to fetch the data and upload it to the specified GCS bucket.
