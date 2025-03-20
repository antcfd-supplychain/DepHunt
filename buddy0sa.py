import os
import json
import requests
import time
from tqdm import tqdm
import concurrent.futures

def ensure_directories(base_dir, ecosystems):
    """Create necessary directories for all ecosystems"""
    for ecosystem in ecosystems:
        os.makedirs(os.path.join(base_dir, ecosystem, "metadata"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, ecosystem, "indexes"), exist_ok=True)

def save_json(data, filepath):
    """Save data as JSON to the specified path"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {str(e)}")
        return False

def load_json(filepath):
    """Load JSON data from the specified path"""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filepath}: {str(e)}")
        return None

def download_with_retry(url, max_retries=3, timeout=30):
    """Download data from URL with retries"""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            elif 500 <= response.status_code < 600:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Server error ({response.status_code}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error: HTTP {response.status_code} for {url}")
                return None
        except requests.exceptions.Timeout:
            retries += 1
            wait_time = 2 ** retries
            print(f"Request timeout, retrying in {wait_time}s...")
            time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None
    
    print(f"Failed to download after {max_retries} retries: {url}")
    return None

def parallel_download(urls, process_func, max_workers=10):
    """Download and process multiple URLs in parallel"""
    results = []
    failed = []
    
    with tqdm(total=len(urls), desc="Downloading") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(download_with_retry, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        result = process_func(url, data)
                        if result:
                            results.append(result)
                    else:
                        failed.append(url)
                except Exception as e:
                    print(f"Error processing {url}: {str(e)}")
                    failed.append(url)
                pbar.update(1)
    
    return results, failed

def print_stats(base_dir, ecosystems):
    """Print statistics about downloaded data"""
    print("\n===== Download Statistics =====")
    
    total_packages = 0
    
    for ecosystem in ecosystems:
        metadata_dir = os.path.join(base_dir, ecosystem, "metadata")
        
        if not os.path.exists(metadata_dir):
            print(f"{ecosystem}: No packages downloaded")
            continue
            
        package_count = len([f for f in os.listdir(metadata_dir) if f.endswith('.json')])
        total_size_mb = sum(os.path.getsize(os.path.join(metadata_dir, f)) 
                           for f in os.listdir(metadata_dir) if f.endswith('.json')) / (1024 * 1024)
        
        print(f"{ecosystem}: {package_count} packages ({total_size_mb:.2f} MB)")
        total_packages += package_count
    
    print(f"\nTotal: {total_packages} packages downloaded")
    print(f"Data location: {os.path.abspath(base_dir)}")


# This file contains intentional security issues for testing SAST tools

def insecure_function_1(user_input):
    # Bandit will detect this as a security issue (B307)
    eval(user_input)  # Insecure!

def insecure_function_2(command):
    # Bandit will detect this as a security issue (B602)
    os.system(command)  # Command injection vulnerability!

def insecure_function_3(data_file):
    # Bandit will detect this as a security issue (B301)
    with open(data_file, 'rb') as f:
        return pickle.load(f)  # Unsafe deserialization!

def sql_injection_example(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"  # Not using parameterization
    return query


# This function is secure and should not trigger any alerts
def secure_function(user_id):
    return f"User ID: {user_id}"