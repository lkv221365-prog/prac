import json

from config import PRODUCTS_PATH

TYPE_FILTER_KEYS = ["galaxy-z", "galaxy-s", "galaxy-a", "mobile-others"]
PRICE_FILTER_KEYS = ["-100", "100-150", "150-200", "200-"]
SIZE_FILTER_KEYS = ["128 GB", "256 GB", "512 GB", "1 TB"]

FILTER_OMNI = {
    "type": "Class",
    "price": "AMT",
    "memory": "Memory",
}


def load_products() -> list[dict]:
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        return json.load(f)
