"""
Extract: Download Boston 311 Service Request CSVs from Analyze Boston.

Downloads 2023 + 2024 datasets (~600K-700K total rows).
Run this once locally — the raw CSVs go into data/raw/.
"""

import os
import requests
from pathlib import Path

# Boston 311 CSV direct download URLs (legacy system, pre-Oct 2025)
DATA_URLS = {
    "2024": "https://data.boston.gov/dataset/8048697b-ad64-4bfc-b090-ee00169f2323/resource/dff4d804-5031-443a-8409-8344efd0e5c8/download/tmpm461rr5o.csv",
    "2023": "https://data.boston.gov/dataset/8048697b-ad64-4bfc-b090-ee00169f2323/resource/b7ea6b1b-3ca4-4c5b-9713-6dc1db52571a/download/tmpa_m8x5s3.csv",
}

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def download_csv(year: str, url: str) -> Path:
    """Download a single year's CSV. Skips if file already exists."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / f"boston_311_{year}.csv"

    if dest.exists():
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  ✓ {dest.name} already exists ({size_mb:.1f} MB) — skipping")
        return dest

    print(f"  ↓ Downloading {year} data...")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r    {pct:.0f}%", end="", flush=True)

    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"\n  ✓ Saved {dest.name} ({size_mb:.1f} MB)")
    return dest


def run():
    print("=" * 50)
    print("RESPONDEX — Extract Phase")
    print("=" * 50)
    print(f"Target directory: {RAW_DIR}\n")

    paths = {}
    for year, url in DATA_URLS.items():
        paths[year] = download_csv(year, url)

    print(f"\nDone. {len(paths)} files ready for transform.")
    return paths


if __name__ == "__main__":
    run()
