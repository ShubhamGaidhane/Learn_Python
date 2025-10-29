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
