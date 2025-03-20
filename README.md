# DepHunt

A multi-ecosystem package metadata bulk downloader for security research.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🔍 Overview

DepHunt is a powerful command-line tool designed for security researchers to efficiently download metadata for packages from multiple ecosystems (npm, PyPI, Maven, Cargo). Whether you need to grab a specific package or bulk-download thousands of packages for analysis, DepHunt makes the process simple and fast.

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/harekrishnarai/DepHunt.git
cd DepHunt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Commands

Download default packages (100 most popular) from all ecosystems:
```bash
python main.py
```

Download from specific ecosystems:
```bash
python main.py --ecosystems npm pypi
```
### Bulk Downloads

Download 1000 packages from npm:
```bash
python main.py --ecosystems npm --bulk --limit 1000
```

Download packages from all ecosystems with increased concurrency:
```bash
python main.py --bulk --limit 500 --concurrency 20
```

### Specific Packages

Download specific packages:
```bash
python main.py --ecosystems pypi --packages requests flask django
```

Download packages from a file (one package name per line):
```bash
python main.py --ecosystems npm --package-file packages.txt
```
### Specific Packages

Download specific packages:
```bash
python main.py --ecosystems pypi --packages requests flask django
```

Download packages from a file (one package name per line):
```bash
python main.py --ecosystems npm --package-file packages.txt
```

## 🔧 Command Options

| Option | Description |
|--------|-------------|
| `--ecosystems` | List of ecosystems to download (`npm`, `pypi`, `maven`, `cargo`) |
| `--bulk` | Download bulk package data (default: False) |
| `--packages` | List of specific package names to download |
| `--package-file` | File containing package names (one per line) |
| `--limit` | Limit number of packages per ecosystem (default: 1000) |
| `--output-dir` | Directory to save downloaded data (default: data) |
| `--concurrency` | Number of concurrent downloads (default: 10) |
| `--resume` | Resume previous download operation (default: False) |

## 📂 Data Structure

Downloaded data is organized as follows:

```
data/
├── npm/
│   ├── metadata/
│   │   ├── package1.json
│   │   ├── package2.json
│   │   └── ...
│   └── indexes/
│       └── npm_packages_index.json
├── pypi/
│   ├── metadata/
│   └── indexes/
├── maven/
│   ├── metadata/
│   └── indexes/
└── cargo/
    ├── metadata/
    └── indexes/
```

## 🌟 Features

- Multi-ecosystem support (npm, PyPI, Maven, Cargo)
- Parallel downloading for high performance
- Resume capability for interrupted downloads
- Support for downloading specific packages or bulk downloads
- Simple command-line interface

## 🧰 Examples

### Security Research Workflow

Download top npm packages and analyze them:
```bash
python main.py --ecosystems npm --bulk --limit 100
# Now you can analyze the downloaded metadata
```

Download a specific list of suspicious packages:
```bash
python main.py --ecosystems npm pypi --package-file suspicious_packages.txt
```
## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.