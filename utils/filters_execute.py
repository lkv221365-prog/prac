import argparse
import json

from playwright.sync_api import Page, expect, sync_playwright

from config import CHECK_TIMEOUT, PRODUCTS_PATH
from utils.filter_counts import SIZE_FILTER_KEYS, build_size_counter, combination_label
from tests.test_filters import (
    _filter_button_for,
    _goto_smartphones,
    ensure_filter_open,
    filter_block_for,
    test_all_combinations_type,
    wait_for_result_count,
)

PRICE_FILTER_KEYS = ["-100", "100-150", "150-200", "200-"]


def load_products() -> list[dict]:
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _with_page(headed: bool, fn) -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        context = browser.new_context(locale="ko-KR")
        page = context.new_page()
        try:
            fn(page)
        finally:
            context.close()
            browser.close()


def _read_result_count(page: Page) -> int:
    locator = page.locator(".pf-top__result-count")
    locator.wait_for(state="visible", timeout=CHECK_TIMEOUT)
    return int(locator.inner_text().strip())


def _run_filter_combinations(
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

        if print_count:
            label = combination_label(filter_keys, current_state)
            count = (
                expected_counts[current_state]
                if expected_counts is not None
                else _read_result_count(page)
            )
            print(f"state={current_state} ({label}): {count}")

        prev_state = current_state


def run_type_filter_test(*, headed: bool = False) -> None:
    _with_page(headed, test_all_combinations_type)


def run_memory_filter_test(*, headed: bool = False) -> None:
    products = load_products()
    expected_counts = build_size_counter(products, SIZE_FILTER_KEYS)

    def _run(page: Page) -> None:
        _goto_smartphones(page)
        _run_filter_combinations(
            page,
            "Memory",
            SIZE_FILTER_KEYS,
            expected_counts=expected_counts,
            print_count=True,
        )

    _with_page(headed, _run)


def run_price_filter_test(*, headed: bool = False) -> None:
    def _run(page: Page) -> None:
        _goto_smartphones(page)
        _run_filter_combinations(
            page,
            "AMT",
            PRICE_FILTER_KEYS,
            print_count=True,
        )

    _with_page(headed, _run)


RUNNERS = {
    "type": run_type_filter_test,
    "memory": run_memory_filter_test,
    "price": run_price_filter_test,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="test_filters.py의 필터 조합 테스트를 일반 스크립트로 실행합니다."
    )
    parser.add_argument(
        "test",
        choices=[*RUNNERS.keys(), "all"],
        help="실행할 테스트 (type / memory / price / all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="브라우저를 화면에 표시하며 실행",
    )
    args = parser.parse_args()

    targets = list(RUNNERS.keys()) if args.test == "all" else [args.test]
    for name in targets:
        print(f"[{name}] 필터 조합 테스트 실행 중...")
        RUNNERS[name](headed=args.headed)
        print(f"[{name}] 완료")


if __name__ == "__main__":
    main()

'''
# 타입 필터만
python -m utils.filters_execute type

# 용량 필터
python -m utils.filters_execute memory

# 가격 필터
python -m utils.filters_execute price

# 전체 실행
python -m utils.filters_execute all --headed

# 브라우저 화면 표시
python -m utils.filters_execute type --headed
'''
