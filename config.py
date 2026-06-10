from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ENV_PATH = ROOT / ".env"

SMARTPHONES_URL = "https://www.samsung.com/sec/smartphones/all-smartphones/"
PRODUCTS_PATH = DATA_DIR / "products.json"
GNB_URLS_PATH = DATA_DIR / "gnb_urls.json"

SLACK_WEBHOOK_ENV_VAR = "SLACK_WEBHOOK_URL"

CHECK_TIMEOUT = 10000
NAV_TIMEOUT = 30000
PAGE_LOAD_WAIT_MS = 3000
