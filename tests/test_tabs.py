from playwright.sync_api import Page, expect
from config import CHECK_TIMEOUT
import re

ACTIVE_CLASS_PATTERN = re.compile(r".*item-actv.*")


def test_galaxy_s_tab_click(smartphones_page: Page):
    galaxy_s_tab = smartphones_page.locator("button[data-lnb-link-url='galaxy-s'][role='tab']")
    expect(galaxy_s_tab).to_have_attribute("aria-selected", "false")

    selected_filter_item = smartphones_page.locator("button.pf-filter__selected-item[data-search-filter='galaxy-s']")
    expect(selected_filter_item).not_to_be_visible()

    galaxy_s_tab.click()
    expect(galaxy_s_tab).to_have_attribute("aria-selected", "true")
    expect(smartphones_page.locator("#pfProductCard")).to_be_visible(timeout=CHECK_TIMEOUT)

    expect(selected_filter_item).to_be_visible(timeout=5000)
    expect(selected_filter_item).to_have_text("갤럭시 S")


def test_galaxy_z_tab_click(smartphones_page: Page):
    galaxy_z_tab = smartphones_page.locator("button[data-lnb-link-url='galaxy-z'][role='tab']")
    expect(galaxy_z_tab).to_have_attribute("aria-selected", "false")

    selected_filter_item = smartphones_page.locator("button.pf-filter__selected-item[data-search-filter='galaxy-z']")
    expect(selected_filter_item).not_to_be_visible()

    galaxy_z_tab.click()
    expect(galaxy_z_tab).to_have_attribute("aria-selected", "true")
    expect(smartphones_page.locator("#pfProductCard")).to_be_visible(timeout=CHECK_TIMEOUT)

    expect(selected_filter_item).to_be_visible(timeout=5000)
    expect(selected_filter_item).to_have_text("갤럭시 Z")


def test_galaxy_a_tab_click(smartphones_page: Page):
    galaxy_a_tab = smartphones_page.locator("button[data-lnb-link-url='galaxy-a'][role='tab']")
    expect(galaxy_a_tab).to_have_attribute("aria-selected", "false")

    selected_filter_item = smartphones_page.locator("button.pf-filter__selected-item[data-search-filter='galaxy-a']")
    expect(selected_filter_item).not_to_be_visible()

    galaxy_a_tab.click()
    expect(galaxy_a_tab).to_have_attribute("aria-selected", "true")
    expect(smartphones_page.locator("#pfProductCard")).to_be_visible(timeout=CHECK_TIMEOUT)

    expect(selected_filter_item).to_be_visible(timeout=5000)
    expect(selected_filter_item).to_have_text("갤럭시 A")


def test_accessories_button_click_and_verify_active_class(smartphones_page: Page):
    accessories_button = smartphones_page.locator("button[data-omni='pf_lnb:sub navi:mobile-accessories']")
    target_li = smartphones_page.locator("li[data-sld-idx='7']").filter(
        has=smartphones_page.locator("a[data-omni='mobile-accessories']")
    )
    expect(target_li).not_to_have_class(ACTIVE_CLASS_PATTERN)

    accessories_button.click()
    expect(target_li).to_have_class(ACTIVE_CLASS_PATTERN, timeout=CHECK_TIMEOUT)
