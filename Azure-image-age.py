import os
import datetime
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import pandas as pd

# Azure authentication credentials
TENANT_ID = 'your_tenant_id'
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'

# CSV output file path
CSV_FILE_PATH = 'image_list.csv'

# Azure subscriptions
SUBSCRIPTIONS = [
    'subscription_id_1',
    'subscription_id_2',
    # Add more subscription IDs here
]

# Initialize Azure credentials and compute client
credentials = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

def get_old_images(compute_client):
    old_images = []
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=60)

    for subscription_id in SUBSCRIPTIONS:
        compute_client.subscription_id = subscription_id
        images = compute_client.images.list()
        
        for image in images:
            if image.creation_data.created_time < cutoff_date:
                old_images.append({
                    'Subscription': subscription_id,
                    'Image Name': image.name,
                    'Creation Date': image.creation_data.created_time
                })

    return old_images

def delete_images(compute_client, images):
    for image in images:
        compute_client.subscription_id = image['Subscription']
        compute_client.images.begin_delete(
            image['Subscription'],
            image['Image Name']
        ).wait()

def save_to_csv(images):
    df = pd.DataFrame(images)
    df.to_csv(CSV_FILE_PATH, index=False)

# Authenticate with Azure and initialize compute client
compute_client = ComputeManagementClient(credentials, SUBSCRIPTIONS[0])

# Get old images and delete them
old_images = get_old_images(compute_client)
delete_images(compute_client, old_images)

# Save old images to a CSV file
save_to_csv(old_images)

print(f"Found {len(old_images)} old images. Deleted and saved details to '{CSV_FILE_PATH}' file.")
