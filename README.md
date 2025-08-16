# Image Compatibility Checker

A Python-based forensic tool that extracts features from VM images and assesses their compatibility with multiple cloud service providers.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Configuration](#configuration)  
7. [Output](#output)  
8. [Reporting](#reporting)  
9. [Contributing](#contributing)  
10. [License](#license)

---

## Overview  
**Image_compatibility_checker** is designed to analyze VM image files, extract metadata and relevant features, and determine whether they're compatible with major cloud platforms such as AWS, Azure, and Google Cloud.

---

## Features  
- Extracts OS information (e.g., distribution, version).  
- Detects bootloader configurations (GRUB, EFI).  
- Identifies installed software and dependencies.  
- Analyzes partition schemes (MBR vs GPT), disk format (e.g., qcow2, vmdk).  
- Compares image attributes against cloud provider requirements.

---

## Requirements  
- Python 3.8 or higher  
- Dependencies listed in `requirements.txt` (e.g., `libguestfs-python`, `boto3`, `azure-sdk`, `google-cloud-storage`)

---

## Installation  
```bash
git clone https://github.com/anant-var/Image_compatibility_checker.git
cd Image_compatibility_checker
pip install -r requirements.txt
```

---

## Usage  
Analyzing a local image file:
```bash
python streamlit_app.py --image /path/to/vm_image.qcow2
```

Or, via command line interface:
```bash
python -m image_compatibility_checker --input /path/to/vm_image.qcow2 --output report.json
```

---

## Configuration  
You can customize behavior via `config.py`:
- Specify cloud target platform(s)
- Set thresholds (e.g., max disk size)
- Enable or disable certain checks (e.g., bootloader, OS version)

---

## Output  
- JSON report summarizing compatibility findings (e.g., `"compatible": true/false`)  
- Detailed logs and feature data dumped to the `reports/` directory  
- A human-readable summary printed in the console or via the Streamlit interface

---

## Reporting  
- Summarized cloud compatibility status  
- List of potential issues with remediation hints  
- Optional CSV or HTML outputs for easier review (configurable)

---

## Contributing  
We appreciate contributions! If you'd like to help:
- Fork the repository  
- Create a feature branch (`git checkout -b feature/new-check`)  
- Submit a pull request with test coverage and documentation updates

---

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
