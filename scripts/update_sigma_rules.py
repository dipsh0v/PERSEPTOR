#!/usr/bin/env python3
"""
PERSEPTOR — SigmaHQ Rule Expansion Script
Downloads Sigma detection rules from the SigmaHQ GitHub repository
and organizes them for the Global Sigma Match engine.

Usage:
    python scripts/update_sigma_rules.py [--output-dir Global_Sigma_Rules]

This expands coverage from ~1,100 process_creation rules to ~3,000-4,000+
rules across all major detection categories.
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
import tempfile
import zipfile
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

SIGMAHQ_ZIP_URL = "https://github.com/SigmaHQ/sigma/archive/refs/heads/master.zip"
SIGMAHQ_API_URL = "https://api.github.com/repos/SigmaHQ/sigma/commits?per_page=1"

# Rule directories to download from SigmaHQ (relative to sigma-master/rules/)
RULE_CATEGORIES = {
    # Windows - comprehensive coverage
    "windows/builtin": "High-value Windows Event Log detections",
    "windows/create_remote_thread": "Remote thread injection (T1055)",
    "windows/create_stream_hash": "ADS / stream hash creation",
    "windows/dns_query": "DNS query detections (C2, exfil domains)",
    "windows/driver_load": "Suspicious driver loading (rootkits)",
    "windows/file_access": "File access anomalies",
    "windows/file_change": "File change monitoring",
    "windows/file_delete": "Suspicious file deletion",
    "windows/file_event": "File system events (drops, staging)",
    "windows/file_rename": "File rename operations",
    "windows/image_load": "DLL side-loading & image load events",
    "windows/network_connection": "Network connections (C2 beaconing)",
    "windows/pipe_created": "Named pipe creation (lateral movement)",
    "windows/powershell": "PowerShell script block logging",
    "windows/process_access": "Process access/injection monitoring",
    "windows/process_creation": "Process creation (already have ~1100)",
    "windows/process_tampering": "Process tampering/hollowing",
    "windows/ps_classic": "PowerShell classic logging",
    "windows/ps_module": "PowerShell module logging",
    "windows/ps_script": "PowerShell script logging",
    "windows/raw_access_thread": "Raw disk access",
    "windows/registry": "Registry modifications (persistence)",
    "windows/sysmon": "Sysmon-specific detections",
    "windows/wmi_event": "WMI event subscriptions (persistence)",
    # Linux
    "linux/auditd": "Linux auditd detections",
    "linux/builtin": "Linux built-in log detections",
    "linux/process_creation": "Linux process creation",
    "linux/network_connection": "Linux network connections",
    "linux/file_event": "Linux file events",
    # macOS
    "macos/builtin": "macOS built-in log detections",
    "macos/process_creation": "macOS process creation",
    # Network
    "network/cisco": "Cisco network device detections",
    "network/dns": "Network DNS detections",
    "network/firewall": "Firewall log detections",
    "network/proxy": "Web proxy detections",
    "network/zeek": "Zeek/Bro IDS detections",
    # Cloud
    "cloud/aws": "AWS CloudTrail detections",
    "cloud/azure": "Azure activity detections",
    "cloud/gcp": "Google Cloud detections",
    "cloud/m365": "Microsoft 365 detections",
    "cloud/okta": "Okta identity detections",
    "cloud/onelogin": "OneLogin detections",
    "cloud/github": "GitHub audit log detections",
    # Web
    "web/webserver": "Web server log detections",
}

# Categories that have nested subdirectories in SigmaHQ
NESTED_CATEGORIES = {
    "windows/builtin",
    "windows/powershell",
    "windows/registry",
}


def download_with_progress(url: str, dest_path: str) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"  Downloading from {url}...")
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "PERSEPTOR-SigmaUpdater/1.0")

        with urllib.request.urlopen(req, timeout=120) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 256  # 256KB chunks

            with open(dest_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r  Progress: {pct:.1f}% ({downloaded // 1024}KB / {total // 1024}KB)", end="", flush=True)

        print()  # newline after progress
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  Error downloading: {e}")
        return False


def extract_rules_from_zip(
    zip_path: str,
    output_dir: str,
    categories: dict,
) -> dict:
    """
    Extract Sigma rule YAML files from the downloaded ZIP.
    Maintains flat structure per category for simplicity.
    Returns stats dict.
    """
    stats = {
        "total_extracted": 0,
        "categories": {},
        "skipped_existing": 0,
        "errors": 0,
    }

    print(f"\n  Extracting rules to {output_dir}...")

    with zipfile.ZipFile(zip_path, "r") as zf:
        all_names = zf.namelist()

        for category_path, description in categories.items():
            # SigmaHQ ZIP internal path: sigma-master/rules/<category>/
            zip_prefix = f"sigma-master/rules/{category_path}/"
            matching_files = [
                n for n in all_names
                if n.startswith(zip_prefix)
                and (n.endswith(".yml") or n.endswith(".yaml"))
                and not n.endswith("/")
            ]

            if not matching_files:
                print(f"  [{category_path}] No rules found (may not exist in this SigmaHQ version)")
                continue

            extracted_count = 0
            for zip_entry in matching_files:
                filename = os.path.basename(zip_entry)
                dest_file = os.path.join(output_dir, filename)

                # Skip if file already exists and is identical
                if os.path.exists(dest_file):
                    try:
                        existing_data = open(dest_file, "rb").read()
                        new_data = zf.read(zip_entry)
                        if hashlib.md5(existing_data).digest() == hashlib.md5(new_data).digest():
                            stats["skipped_existing"] += 1
                            extracted_count += 1
                            continue
                    except Exception:
                        pass

                try:
                    data = zf.read(zip_entry)
                    with open(dest_file, "wb") as f:
                        f.write(data)
                    extracted_count += 1
                except Exception as e:
                    print(f"    Error extracting {filename}: {e}")
                    stats["errors"] += 1

            stats["categories"][category_path] = extracted_count
            stats["total_extracted"] += extracted_count
            print(f"  [{category_path}] {extracted_count} rules — {description}")

    return stats


def get_latest_commit_info() -> dict:
    """Get latest SigmaHQ commit info from GitHub API."""
    try:
        req = urllib.request.Request(SIGMAHQ_API_URL)
        req.add_header("User-Agent", "PERSEPTOR-SigmaUpdater/1.0")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data and len(data) > 0:
                return {
                    "sha": data[0]["sha"][:8],
                    "date": data[0]["commit"]["author"]["date"],
                    "message": data[0]["commit"]["message"].split("\n")[0][:80],
                }
    except Exception:
        pass
    return None


def write_manifest(output_dir: str, stats: dict, commit_info: dict):
    """Write a manifest file with update metadata."""
    manifest = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "source": "SigmaHQ/sigma (GitHub master branch)",
        "source_url": "https://github.com/SigmaHQ/sigma",
        "total_rules": stats["total_extracted"],
        "categories": stats["categories"],
        "errors": stats["errors"],
    }
    if commit_info:
        manifest["sigmahq_commit"] = commit_info

    manifest_path = os.path.join(output_dir, "_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  Manifest written to {manifest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Download and update SigmaHQ detection rules for PERSEPTOR"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: Global_Sigma_Rules in project root)",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        help="Only download specific categories (e.g. windows/dns_query cloud/aws)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )
    args = parser.parse_args()

    # Determine output directory
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        # Auto-detect project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, "Global_Sigma_Rules")

    print("=" * 60)
    print("  PERSEPTOR — SigmaHQ Rule Updater")
    print("=" * 60)
    print(f"  Output: {output_dir}")
    print(f"  Source: {SIGMAHQ_ZIP_URL}")

    # Filter categories if specified
    categories = RULE_CATEGORIES
    if args.categories:
        categories = {k: v for k, v in RULE_CATEGORIES.items() if k in args.categories}
        if not categories:
            print(f"\n  Error: None of the specified categories found.")
            print(f"  Available: {', '.join(RULE_CATEGORIES.keys())}")
            sys.exit(1)

    print(f"  Categories: {len(categories)}")
    print()

    if args.dry_run:
        print("  DRY RUN — would download these categories:")
        for cat, desc in categories.items():
            print(f"    - {cat}: {desc}")
        sys.exit(0)

    # Check latest commit
    print("  Checking SigmaHQ latest commit...")
    commit_info = get_latest_commit_info()
    if commit_info:
        print(f"  Latest: {commit_info['sha']} — {commit_info['message']}")
    else:
        print("  Could not fetch commit info (continuing anyway)")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Download ZIP to temp location
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "sigma-master.zip")

        if not download_with_progress(SIGMAHQ_ZIP_URL, zip_path):
            print("\n  Failed to download SigmaHQ repository. Aborting.")
            sys.exit(1)

        zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"  Downloaded: {zip_size_mb:.1f} MB")

        # Extract rules
        stats = extract_rules_from_zip(zip_path, output_dir, categories)

    # Write manifest
    write_manifest(output_dir, stats, commit_info)

    # Count total files in output dir
    total_files = len([f for f in os.listdir(output_dir) if f.endswith((".yml", ".yaml"))])

    # Summary
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  New rules extracted:  {stats['total_extracted']}")
    print(f"  Unchanged (skipped):  {stats['skipped_existing']}")
    print(f"  Errors:               {stats['errors']}")
    print(f"  Total rules in dir:   {total_files}")
    print()

    # Top categories
    if stats["categories"]:
        sorted_cats = sorted(stats["categories"].items(), key=lambda x: -x[1])
        print("  Top categories:")
        for cat, count in sorted_cats[:10]:
            print(f"    {cat:40s} {count:5d} rules")

    print()
    print("  Done! Restart PERSEPTOR backend to load the new rules.")
    print("=" * 60)


if __name__ == "__main__":
    main()
