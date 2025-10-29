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
