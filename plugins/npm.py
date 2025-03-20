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
        print(f"Downloading {len(package_names)} npm packages...")
        
        # Check for existing packages if resuming
        if resume:
            existing = set(f.split('.')[0] for f in os.listdir(self.metadata_dir) if f.endswith('.json'))
            package_names = [pkg for pkg in package_names if pkg not in existing]
            print(f"Resuming download: {len(package_names)} packages remaining")
        
        # Prepare URL list
        urls = [f"https://registry.npmjs.org/{pkg}" for pkg in package_names]
        
        # Process function for parallel download
        def process_package(url, data):
            pkg_name = url.split('/')[-1]
            filepath = os.path.join(self.metadata_dir, f"{pkg_name}.json")
            save_json(data, filepath)
            return pkg_name
        
        # Download in parallel
        successful, failed = parallel_download(urls, process_package, max_workers=self.concurrency)
        
        print(f"Downloaded {len(successful)} npm packages successfully")
        if failed:
            print(f"Failed to download {len(failed)} packages")
            # Save failed packages list for retry
            save_json({"failed_packages": failed}, os.path.join(self.index_dir, "failed_downloads.json"))
    
    def download_bulk(self, limit=1000, resume=False):
        """Download bulk packages from npm"""
        registry_url = "https://replicate.npmjs.com/_all_docs"
        index_file = os.path.join(self.index_dir, "npm_packages_index.json")
        progress_file = os.path.join(self.index_dir, "bulk_progress.json")
        
        # Check for existing progress
        start_after = None
        if resume and os.path.exists(progress_file):
            progress_data = load_json(progress_file)
            if progress_data and "last_key" in progress_data:
                start_after = progress_data["last_key"]
                print(f"Resuming bulk download from package: {start_after}")
        
        # Get or load package list
        package_names = []
        
        if os.path.exists(index_file) and os.path.getsize(index_file) > 0:
            print("Loading package list from cached index...")
            index_data = load_json(index_file)
            if index_data and "rows" in index_data:
                package_names = [row["id"] for row in index_data["rows"]]
        else:
            print("Downloading npm package index (this may take a while)...")
            
            # NPM has a large registry, so we need to paginate
            total_packages = []
            current_key = start_after
            
            while len(total_packages) < limit:
                params = {"limit": 1000}
                if current_key:
                    params["startkey"] = f'"{current_key}"'
                    params["skip"] = 1
                
                try:
                    response = requests.get(registry_url, params=params)
                    if response.status_code != 200:
                        print(f"Error fetching package list: HTTP {response.status_code}")
                        break
                    
                    data = response.json()
                    if not data.get("rows"):
                        print("No more packages available")
                        break
                    
                    batch_packages = [row["id"] for row in data["rows"]]
                    total_packages.extend(batch_packages)
                    
                    # Save progress
                    current_key = batch_packages[-1]
                    save_json({"last_key": current_key}, progress_file)
                    
                    print(f"Retrieved {len(total_packages)} packages so far...")
                    
                    # Avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error downloading package index: {str(e)}")
                    break
            
            # Save the index for future use
            save_json({"rows": [{"id": pkg} for pkg in total_packages]}, index_file)
            package_names = total_packages
        
        # Limit the number of packages
        package_names = package_names[:limit]
        print(f"Processing {len(package_names)} npm packages...")
        
        # Download the packages
        self.download_packages(package_names, resume)

def download_data():
    """Legacy method for backward compatibility"""
    downloader = PackageDownloader(output_dir=os.path.join("data", "npm"))
    downloader.download_bulk(limit=100)
