import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth
import os

credentials, project = google.auth.default()
print(f"Project: {project}")

regions = [
    'us-central1', 
    'us-west1', 
    'us-east4', 
    'northamerica-northeast1', 
    'europe-west4',
    'asia-northeast1'
]

models_to_try = [
    "gemini-1.5-flash-001",
    "gemini-1.5-pro-preview-0409",
    "gemini-pro"
]

for region in regions:
    print(f"\nScanning Region: {region}")
    try:
        vertexai.init(project=project, location=region)
        for model_name in models_to_try:
            try:
                print(f"  > Checking {model_name}...", end="")
                model = GenerativeModel(model_name)
                # We must generate to test access
                resp = model.generate_content("Hi", stream=False)
                print(" SUCCESS!")
                print(f"FOUND WORKING MODEL: {model_name} in {region}")
                exit(0)
            except Exception as e:
                print(f" Fail. ({str(e)[:100]}...)")
    except Exception as e:
        print(f"  Region init failed: {e}")

print("No working model found in checked regions.")
exit(1)
