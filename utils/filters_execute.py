from playwright.sync_api import Page, sync_playwright
from utils.filter_actions import goto_smartphones, run_filter_combinations
from utils.filter_config import (
    FILTER_OMNI,
    PRICE_FILTER_KEYS,
    TYPE_FILTER_KEYS,
    load_products,
)
from utils.filter_counts import SIZE_FILTER_KEYS, build_size_counter
import argparse


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


def run_type_filter_test(*, headed: bool = False) -> None:
    def _run(page: Page) -> None:
        goto_smartphones(page)
        run_filter_combinations(
            page, FILTER_OMNI["type"], TYPE_FILTER_KEYS, print_count=True
        )

    _with_page(headed, _run)


def run_memory_filter_test(*, headed: bool = False) -> None:
    products = load_products()
    expected_counts = build_size_counter(products, SIZE_FILTER_KEYS)

    def _run(page: Page) -> None:
        goto_smartphones(page)
        run_filter_combinations(
            page,
            FILTER_OMNI["memory"],
            SIZE_FILTER_KEYS,
            expected_counts=expected_counts,
            print_count=True,
        )

    _with_page(headed, _run)


def run_price_filter_test(*, headed: bool = False) -> None:
    def _run(page: Page) -> None:
        goto_smartphones(page)
        run_filter_combinations(
            page, FILTER_OMNI["price"], PRICE_FILTER_KEYS, print_count=True
        )

    _with_page(headed, _run)


RUNNERS = {
    "type": run_type_filter_test,
    "memory": run_memory_filter_test,
    "price": run_price_filter_test,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="필터 조합 테스트를 pytest 없이 CLI로 실행합니다."
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
