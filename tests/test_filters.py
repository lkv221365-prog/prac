from playwright.sync_api import Page, expect
from utils.filter_counts import SIZE_FILTER_KEYS, build_size_counter
from config import CHECK_TIMEOUT, PAGE_LOAD_WAIT_MS, SMARTPHONES_URL
import re

OPEN_CLASS_PATTERN = re.compile(r".*pf-filter__selector-item--(?:open|show).*")
NAV_TIMEOUT = 10000


def filter_block_for(page: Page, omni: str):
    return page.locator(".pf-filter__selector-item").filter(
        has=page.locator(f'button[data-omni="{omni}"]')
    )


def type_filter_block_for(page: Page):
    return filter_block_for(page, "Class")


def _filter_button_for(filter_block):
    return filter_block.locator("button.pf-filter__selector-item-cta")


def ensure_filter_open(_filter_button, filter_block) -> None:
    filter_block.wait_for(state="attached", timeout=CHECK_TIMEOUT)
    button = _filter_button_for(filter_block)
    option = filter_block.locator(".pf-filter__option").first

    try:
        expect(filter_block).to_have_class(OPEN_CLASS_PATTERN, timeout=1500)
        return
    except AssertionError:
        pass

    button.scroll_into_view_if_needed()
    button.click(delay=300)
    try:
        expect(filter_block).to_have_class(OPEN_CLASS_PATTERN, timeout=CHECK_TIMEOUT)
        return
    except AssertionError:
        pass
    expect(option).to_be_visible(timeout=CHECK_TIMEOUT)


def ensure_type_filter_open(filter_button, type_filter_block) -> None:
    ensure_filter_open(filter_button, type_filter_block)


def _goto_smartphones(page: Page) -> None:
    page.goto(SMARTPHONES_URL, wait_until="load", timeout=NAV_TIMEOUT)
    page.wait_for_timeout(PAGE_LOAD_WAIT_MS)


def wait_for_result_count(page: Page, expected: int, timeout: int = CHECK_TIMEOUT) -> None:
    expect(page.locator(".pf-top__result-count")).to_have_text(
        str(expected), timeout=timeout
    )


def _test_all_combinations(
    page: Page,
    omni: str,
    filter_keys: list[str],
    *,
    expected_counts: dict[int, int] | None = None,
    check_timeout: int = 5000,
) -> None:
    n = len(filter_keys)
    filter_block = filter_block_for(page, omni)
    filter_button = _filter_button_for(filter_block)
    filter_button.wait_for(state="visible", timeout=10000)

    ensure_filter_open(filter_button, filter_block)
    page.wait_for_timeout(1500)

    gray_codes = [i ^ (i >> 1) for i in range(2**n)]
    prev_state = 0

    for step, current_state in enumerate(gray_codes):
        filter_block = filter_block_for(page, omni)
        filter_button = _filter_button_for(filter_block)

        if step > 0:
            diff = prev_state ^ current_state
            bit_pos = diff.bit_length()
            changed_index = n - bit_pos

            target_filter = filter_keys[changed_index]
            ensure_filter_open(filter_button, filter_block)
            label = filter_block.locator(f'label[data-search-filter="{target_filter}"]')
            label.dispatch_event("click")
            page.wait_for_timeout(1500)

        ensure_filter_open(filter_button, filter_block)

        for idx, key in enumerate(filter_keys):
            bit_shift = (n - 1) - idx
            expected_checked = ((current_state >> bit_shift) & 1) == 1

            checkbox = filter_block.locator(f'input[data-search-filter="{key}"]')
            if expected_checked:
                expect(checkbox).to_be_checked(timeout=check_timeout)
            else:
                expect(checkbox).not_to_be_checked(timeout=check_timeout)

        if expected_counts is not None:
            wait_for_result_count(
                page, expected_counts[current_state], timeout=check_timeout
            )

        prev_state = current_state


def test_all_combinations_type(page: Page):
    _goto_smartphones(page)
    _test_all_combinations(
        page, "Class", ["galaxy-z", "galaxy-s", "galaxy-a", "mobile-others"]
    )


def test_all_combinations_memory(page: Page, open_json: list[dict]):
    _goto_smartphones(page)
    expected_counts = build_size_counter(open_json, SIZE_FILTER_KEYS)
    _test_all_combinations(
        page,
        "Memory",
        SIZE_FILTER_KEYS,
        expected_counts=expected_counts,
    )


def test_all_combinations_price(page: Page):
    _goto_smartphones(page)
    _test_all_combinations(
        page, "AMT", ["-100", "100-150", "150-200", "200-"]
    )