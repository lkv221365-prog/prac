from playwright.sync_api import Page, expect
from config import CHECK_TIMEOUT, PAGE_LOAD_WAIT_MS, SMARTPHONES_URL

SOURCE_TITLE_SELECTOR = "dt[data-device='pc']"
TARGET_TITLE_SELECTOR = ".pf-head-title h2[data-device='pc']"

NAV_SLIDE_IDX_START = 1
NAV_SLIDE_IDX_END = 7

def _nav_item_selector(slide_idx: int) -> str:
    return f"li.pf-m-nav-item[data-sld-idx='{slide_idx}']"


def test_nav_link_and_landing_page_verification(smartphones_page: Page):
    for slide_idx in range(NAV_SLIDE_IDX_START, NAV_SLIDE_IDX_END + 1):
        nav_item = smartphones_page.locator(_nav_item_selector(slide_idx))
        expect(nav_item).to_be_visible(timeout=CHECK_TIMEOUT)

        nav_link = nav_item.locator("a")
        expect(nav_link).to_be_visible(timeout=CHECK_TIMEOUT)

        target_url = nav_link.get_attribute("href")
        expected_title = nav_link.locator(SOURCE_TITLE_SELECTOR).text_content()

        assert target_url, f"data-sld-idx={slide_idx}: URL(href)을 추출하지 못했습니다."
        assert expected_title, f"data-sld-idx={slide_idx}: 카테고리명을 추출하지 못했습니다."
        expected_title = expected_title.strip()

        smartphones_page.goto(target_url, wait_until="load", timeout=CHECK_TIMEOUT)

        target_title_locator = smartphones_page.locator(TARGET_TITLE_SELECTOR)
        expect(target_title_locator).to_be_visible(timeout=CHECK_TIMEOUT)
        expect(target_title_locator).to_have_text(expected_title, timeout=CHECK_TIMEOUT)

        smartphones_page.goto(SMARTPHONES_URL, wait_until="load", timeout=CHECK_TIMEOUT)
        smartphones_page.wait_for_timeout(PAGE_LOAD_WAIT_MS)
