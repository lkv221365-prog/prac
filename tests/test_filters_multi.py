from dataclasses import dataclass
from playwright.sync_api import Page
from utils.filter_actions import (
    goto_smartphones,
    set_filter_selection,
    wait_for_result_count,
)
from utils.filter_config import (
    FILTER_OMNI,
    PRICE_FILTER_KEYS,
    SIZE_FILTER_KEYS,
    TYPE_FILTER_KEYS,
)
import pytest


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


def _apply_multi_filters(page: Page, case: MultiFilterCase) -> None:
    set_filter_selection(
        page, FILTER_OMNI["type"], TYPE_FILTER_KEYS, case.type_filters
    )
    set_filter_selection(
        page, FILTER_OMNI["price"], PRICE_FILTER_KEYS, case.price_filters
    )
    set_filter_selection(
        page, FILTER_OMNI["memory"], SIZE_FILTER_KEYS, case.size_filters
    )


@pytest.mark.parametrize(
    "case",
    MULTI_FILTER_CASES,
    ids=[case.id for case in MULTI_FILTER_CASES],
)
def test_multi_filter_combination(page: Page, case: MultiFilterCase) -> None:
    goto_smartphones(page)
    _apply_multi_filters(page, case)
    wait_for_result_count(page, case.expected_count)
