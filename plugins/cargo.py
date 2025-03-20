import os
import json
import time
import requests
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
        print(f"Downloading {len(package_names)} Cargo packages...")
        
        # Check for existing packages if resuming
        if resume:
            existing = set(f.split('.')[0] for f in os.listdir(self.metadata_dir) if f.endswith('.json'))
            package_names = [pkg for pkg in package_names if pkg not in existing]
            print(f"Resuming download: {len(package_names)} packages remaining")
        
        # Prepare URL list
        urls = [f"https://crates.io/api/v1/crates/{pkg}" for pkg in package_names]
        
        # Process function for parallel download
        def process_package(url, data):
            pkg_name = url.split('/')[-1]
            filepath = os.path.join(self.metadata_dir, f"{pkg_name}.json")
            save_json(data, filepath)
            return pkg_name
        
        # Download in parallel
        successful, failed = parallel_download(urls, process_package, max_workers=self.concurrency)
        
        print(f"Downloaded {len(successful)} Cargo packages successfully")
        if failed:
            print(f"Failed to download {len(failed)} packages")
            failed_pkgs = [url.split('/')[-1] for url in failed]
            save_json({"failed_packages": failed_pkgs}, os.path.join(self.index_dir, "failed_downloads.json"))
    
    def download_bulk(self, limit=1000, resume=False):
        """Download bulk packages from crates.io"""
        index_file = os.path.join(self.index_dir, "cargo_packages_index.json")
        
        # Get or load package list
        package_names = []
        
        if os.path.exists(index_file) and os.path.getsize(index_file) > 0:
            print("Loading package list from cached index...")
            index_data = load_json(index_file)
            if index_data:
                package_names = index_data
        else:
            print("Downloading Cargo package index...")
            
            # Use crates.io API to get packages in batches
            page = 1
            per_page = 100
            total_fetched = 0
            
            while total_fetched < limit:
                try:
                    url = f"https://crates.io/api/v1/crates?page={page}&per_page={per_page}&sort=downloads"
                    response = requests.get(url)
                    
                    if response.status_code != 200:
                        print(f"Error fetching package list: HTTP {response.status_code}")
                        break
                    
                    data = response.json()
                    crates = data.get("crates", [])
                    if not crates:
                        break
                    
                    for crate in crates:
                        package_names.append(crate["name"])
                    
                    total_fetched += len(crates)
                    print(f"Fetched {total_fetched} packages so far...")
                    
                    page += 1
                    time.sleep(1)  # Be nice to the API
                    
                except Exception as e:
                    print(f"Error downloading package index: {str(e)}")
                    break
            
            # Save the index for future use
            save_json(package_names, index_file)
        
        # Limit the number of packages
        package_names = package_names[:limit]
        print(f"Processing {len(package_names)} Cargo packages...")
        
        # Download the packages
        self.download_packages(package_names, resume)

def download_data():
    """Legacy method for backward compatibility"""
    downloader = PackageDownloader(output_dir=os.path.join("data", "cargo"))
    downloader.download_bulk(limit=100)
