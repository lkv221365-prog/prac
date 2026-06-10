from dataclasses import dataclass
from utils.filter_counts import SIZE_FILTER_KEYS
from playwright.sync_api import Page, expect
from config import CHECK_TIMEOUT
from tests.test_filters import (
    _filter_button_for,
    _goto_smartphones,
    ensure_filter_open,
    filter_block_for,
    wait_for_result_count,
)
import pytest

TYPE_FILTER_KEYS = ["galaxy-z", "galaxy-s", "galaxy-a", "mobile-others"]
PRICE_FILTER_KEYS = ["-100", "100-150", "150-200", "200-"]


@dataclass(frozen=True)
class MultiFilterCase:
    id: str
    type_filters: tuple[str, ...]
    price_filters: tuple[str, ...]
    size_filters: tuple[str, ...]
    expected_count: int


MULTI_FILTER_CASES = [
    MultiFilterCase(
        id="tc1_type_z_s_price_100_150",
        type_filters=("galaxy-z", "galaxy-s"),
        price_filters=("100-150",),
        size_filters=(),
        expected_count=32,
    ),
    MultiFilterCase(
        id="tc2_type_s_size_128_256",
        type_filters=("galaxy-s",),
        price_filters=(),
        size_filters=("128 GB", "256 GB"),
        expected_count=36,
    ),
    MultiFilterCase(
        id="tc3_type_s_size_128_256_price_100_150_150_200",
        type_filters=("galaxy-s",),
        price_filters=("100-150", "150-200"),
        size_filters=("128 GB", "256 GB"),
        expected_count=29,
    ),
    MultiFilterCase(
        id="tc4_type_a_size_1tb_price_200",
        type_filters=("galaxy-a",),
        price_filters=("200-",),
        size_filters=("1 TB",),
        expected_count=0,
    ),
]


def _set_filter_selection(
    page: Page,
    omni: str,
    all_keys: list[str],
    selected_keys: tuple[str, ...],
    *,
    check_timeout: int = CHECK_TIMEOUT,
) -> None:
    filter_block = filter_block_for(page, omni)
    filter_button = _filter_button_for(filter_block)
    filter_button.wait_for(state="visible", timeout=CHECK_TIMEOUT)

    ensure_filter_open(filter_button, filter_block)
    page.wait_for_timeout(1500)

    selected = set(selected_keys)
    for key in all_keys:
        filter_block = filter_block_for(page, omni)
        checkbox = filter_block.locator(f'input[data-search-filter="{key}"]')
        expected_checked = key in selected

        if checkbox.is_checked() != expected_checked:
            label = filter_block.locator(f'label[data-search-filter="{key}"]')
            label.dispatch_event("click")
            page.wait_for_timeout(1500)

        if expected_checked:
            expect(checkbox).to_be_checked(timeout=check_timeout)
        else:
            expect(checkbox).not_to_be_checked(timeout=check_timeout)


def _apply_multi_filters(page: Page, case: MultiFilterCase) -> None:
    _set_filter_selection(page, "Class", TYPE_FILTER_KEYS, case.type_filters)
    _set_filter_selection(page, "AMT", PRICE_FILTER_KEYS, case.price_filters)
    _set_filter_selection(page, "Memory", SIZE_FILTER_KEYS, case.size_filters)


@pytest.mark.parametrize(
    "case",
    MULTI_FILTER_CASES,
    ids=[case.id for case in MULTI_FILTER_CASES],
)
def test_multi_filter_combination(page: Page, case: MultiFilterCase) -> None:
    _goto_smartphones(page)
    _apply_multi_filters(page, case)
    wait_for_result_count(page, case.expected_count)
