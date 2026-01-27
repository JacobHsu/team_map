import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

SCREENSHOTONE_API = "https://api.screenshotone.com/take"

TARGETS = [
    {
        "name": "oddsportal_nba",
        "url": "https://www.oddsportal.com/basketball/usa/nba/",
        "selector": ".empty\\:min-h-\\[80vh\\]",  # Table area
        "block_ads": True,
        "block_cookie_banners": True,
    },
]


def build_screenshot_url(target: dict) -> str:
    """Build ScreenshotOne API URL"""
    params = {
        "access_key": os.getenv("SCREENSHOTONE_ACCESS_KEY"),
        "url": target["url"],
        "format": os.getenv("SCREENSHOT_FORMAT", "png"),
        "block_ads": str(target.get("block_ads", True)).lower(),
        "block_cookie_banners": str(target.get("block_cookie_banners", True)).lower(),
        "viewport_width": 1920,
        "viewport_height": 1080,
        "delay": 3,  # Wait for page to load
    }

    if target.get("selector"):
        params["selector"] = target["selector"]

    return f"{SCREENSHOTONE_API}?{urlencode(params)}"


def download_screenshot(target: dict, output_dir: str = "screenshots") -> str:
    """Download screenshot and save to file

    Filename uses day of month (01-31) for automatic monthly rotation.
    e.g., oddsportal_nba_27.png - will be overwritten next month on the 27th.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    url = build_screenshot_url(target)
    day_of_month = datetime.now().strftime("%d")  # 01-31
    filename = f"{target['name']}_{day_of_month}.png"
    filepath = Path(output_dir) / filename

    print(f"Fetching: {target['name']}")
    print(f"URL: {target['url']}")

    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        filepath.write_bytes(response.content)
        print(f"Saved: {filepath}")
        return str(filepath)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def main():
    if not os.getenv("SCREENSHOTONE_ACCESS_KEY"):
        print("Error: SCREENSHOTONE_ACCESS_KEY not set in .env")
        return

    print(f"Screenshot run: {datetime.now().isoformat()}")
    print("-" * 50)

    results = []
    for target in TARGETS:
        filepath = download_screenshot(target)
        if filepath:
            results.append(filepath)
        print("-" * 50)

    print(f"Completed: {len(results)}/{len(TARGETS)} screenshots")


if __name__ == "__main__":
    main()
