from playwright.sync_api import Page
from utils.filter_actions import goto_smartphones, run_filter_combinations
from utils.filter_config import FILTER_OMNI, PRICE_FILTER_KEYS, TYPE_FILTER_KEYS
from utils.filter_counts import SIZE_FILTER_KEYS, build_size_counter


def test_all_combinations_type(page: Page):
    goto_smartphones(page)
    run_filter_combinations(page, FILTER_OMNI["type"], TYPE_FILTER_KEYS)


def test_all_combinations_memory(page: Page, open_json: list[dict]):
    goto_smartphones(page)
    expected_counts = build_size_counter(open_json, SIZE_FILTER_KEYS)
    run_filter_combinations(
        page,
        FILTER_OMNI["memory"],
        SIZE_FILTER_KEYS,
        expected_counts=expected_counts,
    )


def test_all_combinations_price(page: Page):
    goto_smartphones(page)
    run_filter_combinations(page, FILTER_OMNI["price"], PRICE_FILTER_KEYS)
