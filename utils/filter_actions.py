import re

from playwright.sync_api import Page, expect

from config import CHECK_TIMEOUT, NAV_TIMEOUT, PAGE_LOAD_WAIT_MS, SMARTPHONES_URL
from utils.filter_counts import combination_label

OPEN_CLASS_PATTERN = re.compile(r".*pf-filter__selector-item--(?:open|show).*")


def filter_block_for(page: Page, omni: str):
    return page.locator(".pf-filter__selector-item").filter(
        has=page.locator(f'button[data-omni="{omni}"]')
    )


def filter_button_for(filter_block):
    return filter_block.locator("button.pf-filter__selector-item-cta")


def ensure_filter_open(_filter_button, filter_block) -> None:
    filter_block.wait_for(state="attached", timeout=CHECK_TIMEOUT)
    button = filter_button_for(filter_block)
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


def goto_smartphones(page: Page) -> None:
    page.goto(SMARTPHONES_URL, wait_until="load", timeout=NAV_TIMEOUT)
    page.wait_for_timeout(PAGE_LOAD_WAIT_MS)


def wait_for_result_count(page: Page, expected: int, timeout: int = CHECK_TIMEOUT) -> None:
    expect(page.locator(".pf-top__result-count")).to_have_text(
        str(expected), timeout=timeout
    )


def read_result_count(page: Page) -> int:
    locator = page.locator(".pf-top__result-count")
    locator.wait_for(state="visible", timeout=CHECK_TIMEOUT)
    return int(locator.inner_text().strip())


def set_filter_selection(
    page: Page,
    omni: str,
    all_keys: list[str],
    selected_keys: tuple[str, ...],
    *,
    check_timeout: int = CHECK_TIMEOUT,
) -> None:
    filter_block = filter_block_for(page, omni)
    filter_button = filter_button_for(filter_block)
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


def run_filter_combinations(
    page: Page,
    omni: str,
    filter_keys: list[str],
    *,
    expected_counts: dict[int, int] | None = None,
    check_timeout: int = 5000,
    print_count: bool = False,
) -> None:
    n = len(filter_keys)
    filter_block = filter_block_for(page, omni)
    filter_button = filter_button_for(filter_block)
    filter_button.wait_for(state="visible", timeout=CHECK_TIMEOUT)

    ensure_filter_open(filter_button, filter_block)
    page.wait_for_timeout(1500)

    gray_codes = [i ^ (i >> 1) for i in range(2**n)]
    prev_state = 0

    for step, current_state in enumerate(gray_codes):
        filter_block = filter_block_for(page, omni)
        filter_button = filter_button_for(filter_block)

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

        if print_count:
            label = combination_label(filter_keys, current_state)
            count = (
                expected_counts[current_state]
                if expected_counts is not None
                else read_result_count(page)
            )
            print(f"state={current_state} ({label}): {count}")

        prev_state = current_state
