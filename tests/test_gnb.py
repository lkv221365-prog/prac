from playwright.sync_api import Page, expect
from config import CHECK_TIMEOUT, NAV_TIMEOUT
from crawlers.gnb_crawler import load_gnb_urls, url_test_id
import pytest


def pytest_generate_tests(metafunc):
    if "target_url" not in metafunc.fixturenames:
        return

    urls = load_gnb_urls()
    if not urls:
        pytest.skip(
            "data/gnb_urls.json이 비어 있습니다. "
            "`python -m crawlers.gnb_crawler`로 URL 목록을 먼저 생성하세요.",
            allow_module_level=True,
        )

    metafunc.parametrize(
        "target_url",
        urls,
        ids=[url_test_id(url) for url in urls],
    )


def test_gnb_url_verification(smartphones_page: Page, target_url: str):
    response = smartphones_page.goto(
        target_url,
        wait_until="domcontentloaded",
        timeout=NAV_TIMEOUT,
    )

    assert response is not None, f"페이지 응답 없음 (로드 실패): {target_url}"
    assert response.ok, f"잘못된 페이지 접근 (HTTP Status: {response.status}): {target_url}"
    expect(smartphones_page.locator("body")).to_be_visible(timeout=CHECK_TIMEOUT)
