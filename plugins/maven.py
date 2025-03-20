import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from utils import save_json, load_json, download_with_retry, parallel_download
from tqdm import tqdm

class PackageDownloader:
    def __init__(self, output_dir, concurrency=10):
        self.output_dir = output_dir
        self.metadata_dir = os.path.join(output_dir, "metadata")
        self.index_dir = os.path.join(output_dir, "indexes")
        self.concurrency = concurrency
        
        # Ensure directories exist
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
    
    def download_packages(self, package_names, resume=False):
        """Download metadata for specific package names"""
        print(f"Downloading {len(package_names)} Maven packages...")
        
        # Check for existing packages if resuming
        if resume:
            existing = set(f.split('.')[0] for f in os.listdir(self.metadata_dir) if f.endswith('.json'))
            package_names = [pkg for pkg in package_names if pkg not in existing]
            print(f"Resuming download: {len(package_names)} packages remaining")
        
        successful = []
        failed = []
        
        # Maven packages require different handling than npm/pypi
        for package in tqdm(package_names, desc="Downloading Maven packages"):
            try:
                # For Maven, package names are typically in group:artifact format
                if ":" in package:
                    group_id, artifact_id = package.split(":")
                    group_path = group_id.replace(".", "/")
                    
                    # First get the maven-metadata.xml to find latest version
                    metadata_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
                    metadata_response = requests.get(metadata_url)
                    
                    if metadata_response.status_code != 200:
                        failed.append(package)
                        continue
                    
                    # Parse XML to find latest version
                    root = ET.fromstring(metadata_response.text)
                    latest_version = root.find(".//release").text if root.find(".//release") is not None else root.find(".//version").text
                    
                    # Get the POM file for the latest version
                    pom_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{latest_version}/{artifact_id}-{latest_version}.pom"
                    pom_response = requests.get(pom_url)
                    
                    if pom_response.status_code != 200:
                        failed.append(package)
                        continue
                    
                    # Convert the package data to JSON format
                    package_data = {
                        "group_id": group_id,
                        "artifact_id": artifact_id,
                        "latest_version": latest_version,
                        "pom_content": pom_response.text
                    }
                    
                    # Save as JSON
                    filepath = os.path.join(self.metadata_dir, f"{group_id}_{artifact_id}.json")
                    save_json(package_data, filepath)
                    successful.append(package)
                else:
                    # Handle incorrect format
                    print(f"Invalid Maven package format: {package}, expected 'group:artifact'")
                    failed.append(package)
            
            except Exception as e:
                print(f"Error downloading Maven package {package}: {str(e)}")
                failed.append(package)
        
        print(f"Downloaded {len(successful)} Maven packages successfully")
        if failed:
            print(f"Failed to download {len(failed)} packages")
            save_json({"failed_packages": failed}, os.path.join(self.index_dir, "failed_downloads.json"))
    
    def download_bulk(self, limit=1000, resume=False):
        """Download bulk packages from Maven Central"""
        index_file = os.path.join(self.index_dir, "maven_packages_index.json")
        
        # Get or load package list
        package_names = []
        
        if os.path.exists(index_file) and os.path.getsize(index_file) > 0:
            print("Loading package list from cached index...")
            index_data = load_json(index_file)
            if index_data:
                package_names = index_data
        else:
            print("Downloading Maven package index...")
            
            # Maven doesn't have a simple API for all packages
            # We'll use the search API to get popular packages
            try:
                # Start with some popular groups
                popular_groups = [
                    "org.apache", "com.google", "org.springframework",
                    "io.quarkus", "org.hibernate", "com.fasterxml.jackson",
                    "org.junit", "io.micronaut", "org.slf4j"
                ]
                
                for group in tqdm(popular_groups, desc="Fetching group artifacts"):
                    # Search for artifacts in this group
                    search_url = f"https://search.maven.org/solrsearch/select?q=g:{group}&rows=1000&wt=json"
                    response = requests.get(search_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        docs = data.get("response", {}).get("docs", [])
                        
                        for doc in docs:
                            g = doc.get("g")
                            a = doc.get("a")
                            if g and a:
                                package_names.append(f"{g}:{a}")
                        
                        time.sleep(1)  # Avoid rate limiting
                
                # Save the index for future use
                save_json(package_names, index_file)
                print(f"Found {len(package_names)} Maven packages")
            
            except Exception as e:
                print(f"Error downloading package index: {str(e)}")
        
        # Limit the number of packages
        package_names = package_names[:limit]
        print(f"Processing {len(package_names)} Maven packages...")
        
        # Download the packages
        self.download_packages(package_names, resume)

def download_data():
    """Legacy method for backward compatibility"""
    downloader = PackageDownloader(output_dir=os.path.join("data", "maven"))
    downloader.download_bulk(limit=100)
