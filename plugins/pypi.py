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
        print(f"Downloading {len(package_names)} PyPI packages...")
        
        # Check for existing packages if resuming
        if resume:
            existing = set(f.split('.')[0] for f in os.listdir(self.metadata_dir) if f.endswith('.json'))
            package_names = [pkg for pkg in package_names if pkg not in existing]
            print(f"Resuming download: {len(package_names)} packages remaining")
        
        # Prepare URL list
        urls = [f"https://pypi.org/pypi/{pkg}/json" for pkg in package_names]
        
        # Process function for parallel download
        def process_package(url, data):
            pkg_name = url.split('/')[-2]
            filepath = os.path.join(self.metadata_dir, f"{pkg_name}.json")
            save_json(data, filepath)
            return pkg_name
        
        # Download in parallel
        successful, failed = parallel_download(urls, process_package, max_workers=self.concurrency)
        
        print(f"Downloaded {len(successful)} PyPI packages successfully")
        if failed:
            print(f"Failed to download {len(failed)} packages")
            failed_pkgs = [url.split('/')[-2] for url in failed]
            save_json({"failed_packages": failed_pkgs}, os.path.join(self.index_dir, "failed_downloads.json"))
    
    def download_bulk(self, limit=1000, resume=False):
        """Download bulk packages from PyPI"""
        index_file = os.path.join(self.index_dir, "pypi_packages_index.json")
        
        # Get or load package list
        package_names = []
        
        if os.path.exists(index_file) and os.path.getsize(index_file) > 0:
            print("Loading package list from cached index...")
            index_data = load_json(index_file)
            if index_data:
                package_names = index_data
        else:
            print("Downloading PyPI package index...")
            
            try:
                # PyPI provides a simple API for all projects
                response = requests.get("https://pypi.org/simple/")
                if response.status_code == 200:
                    # Parse the simple HTML response to extract package names
                    # Note: This is a basic approach - ideally use a proper HTML parser
                    html = response.text
                    lines = html.split("\n")
                    for line in lines:
                        if 'href="/simple/' in line:
                            pkg = line.split('href="/simple/')[1].split('/')[0]
                            package_names.append(pkg)
                    
                    print(f"Found {len(package_names)} PyPI packages")
                    
                    # Save the index for future use
                    save_json(package_names, index_file)
                else:
                    print(f"Error fetching package list: HTTP {response.status_code}")
            
            except Exception as e:
                print(f"Error downloading package index: {str(e)}")
        
        # Limit the number of packages
        package_names = package_names[:limit]
        print(f"Processing {len(package_names)} PyPI packages...")
        
        # Download the packages
        self.download_packages(package_names, resume)

def download_data():
    """Legacy method for backward compatibility"""
    downloader = PackageDownloader(output_dir=os.path.join("data", "pypi"))
    downloader.download_bulk(limit=100)
