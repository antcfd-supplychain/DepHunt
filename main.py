import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from plugins import npm, pypi, maven, cargo
from utils import ensure_directories, print_stats

def main():
    parser = argparse.ArgumentParser(description="DepHunt: Multi-Ecosystem Package Bulk Downloader")
    parser.add_argument("--ecosystems", nargs="+", choices=["npm", "pypi", "maven", "cargo"],
                        default=["npm", "pypi", "maven", "cargo"],
                        help="List of ecosystems to download (default: all)")
    parser.add_argument("--bulk", action="store_true", 
                        help="Download bulk package data (top packages by default)")
    parser.add_argument("--packages", nargs="+", help="List of specific package names to download")
    parser.add_argument("--package-file", type=str, 
                        help="File containing package names (one per line)")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Limit number of packages to download per ecosystem (default: 1000)")
    parser.add_argument("--output-dir", type=str, default="data",
                        help="Directory to save downloaded data (default: data)")
    parser.add_argument("--concurrency", type=int, default=10,
                        help="Number of concurrent downloads (default: 10)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume previous download operation")
    
    args = parser.parse_args()
    
    # Ensure all necessary directories exist
    ensure_directories(args.output_dir, args.ecosystems)
    
    # Load packages from file if specified
    package_list = []
    if args.package_file and os.path.exists(args.package_file):
        with open(args.package_file, 'r') as f:
            package_list = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(package_list)} packages from {args.package_file}")
    
    # Add packages from command line
    if args.packages:
        package_list.extend(args.packages)
    
    # Set up downloaders for each ecosystem
    downloaders = {
        "npm": npm.PackageDownloader(
            output_dir=os.path.join(args.output_dir, "npm"),
            concurrency=args.concurrency
        ),
        "pypi": pypi.PackageDownloader(
            output_dir=os.path.join(args.output_dir, "pypi"),
            concurrency=args.concurrency
        ),
        "maven": maven.PackageDownloader(
            output_dir=os.path.join(args.output_dir, "maven"),
            concurrency=args.concurrency
        ),
        "cargo": cargo.PackageDownloader(
            output_dir=os.path.join(args.output_dir, "cargo"),
            concurrency=args.concurrency
        )
    }
    
    # Process each ecosystem
    for ecosystem in args.ecosystems:
        print(f"\n===== Processing {ecosystem} packages =====")
        downloader = downloaders.get(ecosystem)
        
        if package_list:
            # Download specific packages
            downloader.download_packages(package_list, resume=args.resume)
        elif args.bulk:
            # Download bulk packages
            downloader.download_bulk(limit=args.limit, resume=args.resume)
        else:
            # Download default set of popular packages
            default_limit = 100  # A reasonable default
            print(f"Downloading top {default_limit} {ecosystem} packages...")
            downloader.download_bulk(limit=default_limit, resume=args.resume)
    
    # Print summary statistics
    print_stats(args.output_dir, args.ecosystems)

if __name__ == "__main__":
    main()
