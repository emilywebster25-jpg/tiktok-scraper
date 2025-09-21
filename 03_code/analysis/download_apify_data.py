#!/usr/bin/env python3
"""
Script to download TikTok data from Apify and organize by search keyword
"""
import requests
import json
import os
from datetime import datetime

# ===== STEP 1: Add your Apify API key here =====
# You can find this at: https://console.apify.com/account/integrations
APIFY_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# Create a folder for downloaded data
output_folder = "apify_downloads"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def get_all_datasets():
    """Get list of all your datasets from Apify"""
    url = "https://api.apify.com/v2/actor-runs"
    params = {
        'token': APIFY_API_KEY,
        'status': 'SUCCEEDED',
        'limit': 1000
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching datasets: {e}")
        return None

def download_dataset(dataset_id, search_query):
    """Download a specific dataset"""
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
    params = {'token': APIFY_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Save the data
        filename = f"{output_folder}/{search_query}_{dataset_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)

        print(f"✅ Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {dataset_id}: {e}")
        return False

if __name__ == "__main__":
    if APIFY_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ Please add your Apify API key to the script first!")
        exit(1)

    print("🔍 Fetching datasets from Apify...")
    datasets = get_all_datasets()

    if datasets:
        print(f"📊 Found {len(datasets.get('data', []))} datasets")
        for dataset in datasets.get('data', []):
            dataset_id = dataset.get('defaultDatasetId')
            search_query = dataset.get('buildId', 'unknown')
            if dataset_id:
                download_dataset(dataset_id, search_query)
    else:
        print("❌ Failed to fetch datasets")