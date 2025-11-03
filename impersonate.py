import requests
from google.auth import default, impersonated_credentials
from google.auth.transport.requests import Request

SERVICE_URL = "https://ingest-api-to-gcs-********a-uc.a.run.app"
TARGET_SA = "service-46*************@gcf-admin-robot.iam.gserviceaccount.com"

def get_id_token(audience: str) -> str:
    src, _ = default()  # after: gcloud auth application-default login

    # Create impersonated credentials
    target_creds = impersonated_credentials.Credentials(
        source_credentials=src,
        target_principal=TARGET_SA,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        lifetime=3600,
    )

    # Create ID token credentials from the impersonated credentials
    id_creds = impersonated_credentials.IDTokenCredentials(
        target_credentials=target_creds,
        target_audience=audience,
        include_email=True,
    )

    request = Request()
    id_creds.refresh(request)
    return id_creds.token

def main():
    token = get_id_token(SERVICE_URL)
    r = requests.post(
        SERVICE_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={
            "api_url":"https://jsonplaceholder.typicode.com/posts",
            "gcs_uri":"gs://agent-artifact-files/API_Data/posts_002.csv",
        },
        timeout=120,
    )
    r.raise_for_status()
    print(r.text)

if __name__ == "__main__":
    main()
