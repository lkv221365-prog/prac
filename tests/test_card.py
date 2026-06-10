from config import CHECK_TIMEOUT
from playwright.sync_api import Locator, Page, expect
from utils import scroll_for_lazyload_sync
import pytest

DOM_UPDATE_WAIT_MS = 1500
CARD_SELECTOR = "#pfProductCard > .pf-product-card__row, #pfProductCard > [id^='li-prd']"
COLOR_BUTTONS_SELECTOR = "[id^='itm-color-']"
COLOR_TEXT_SELECTOR = ".pf-option-selector__color-name .pf-option-selector__color-tooltip-text"
CAPACITY_BUTTONS_SELECTOR = "[id^='itm-contract-']"
PRICE_TEXT_SELECTOR = ".pf-product__price .price-won > span"
COMPARE_WRAPPER_SELECTOR = ".pf-product-card__compare"
COMPARE_LABEL_SELECTOR = "label.pf-checkbox__label"
COMPARE_LAYER_SELECTOR = "#pfpd-compare"
COMPARE_LAYER_WAIT_MS = 1000


def _get_first_card_with(page: Page, option_selector: str) -> Locator:
    return page.locator(CARD_SELECTOR).filter(has=page.locator(option_selector)).first


def _is_already_selected(option_button: Locator) -> bool:
    parent_div = option_button.locator("xpath=..")
    class_attr = parent_div.get_attribute("class") or ""
    return "is-checked" in class_attr


def _dispatch_swiper_click(option_input: Locator) -> None:
    option_input.scroll_into_view_if_needed()
    expect(option_input).to_be_attached(timeout=CHECK_TIMEOUT)
    option_input.dispatch_event("click")


def _assert_option_changes(
    page: Page,
    *,
    option_selector: str,
    value_selector: str,
    skip_reason: str,
) -> None:
    first_card = _get_first_card_with(page, option_selector)
    first_card.scroll_into_view_if_needed()
    expect(first_card).to_be_visible(timeout=CHECK_TIMEOUT)

    option_count = first_card.locator(option_selector).count()
    if option_count <= 1:
        pytest.skip(skip_reason)

    for click_round in range(option_count):
        current_card = _get_first_card_with(page, option_selector)
        current_card.scroll_into_view_if_needed()

        target_button = current_card.locator(option_selector).nth(click_round)
        if _is_already_selected(target_button):
            continue

        value_locator = current_card.locator(value_selector)
        previous_value = value_locator.text_content().strip()

        _dispatch_swiper_click(target_button)
        page.wait_for_timeout(DOM_UPDATE_WAIT_MS)

        updated_card = _get_first_card_with(page, option_selector)
        updated_card.scroll_into_view_if_needed()
        updated_value_locator = updated_card.locator(value_selector)

        expect(updated_value_locator).not_to_have_text(previous_value, timeout=CHECK_TIMEOUT)


def test_color_option_change(smartphones_page: Page):
    scroll_for_lazyload_sync(smartphones_page)
    _assert_option_changes(
        smartphones_page,
        option_selector=COLOR_BUTTONS_SELECTOR,
        value_selector=COLOR_TEXT_SELECTOR,
        skip_reason="색상 옵션이 1개 이하여서 변경 검증을 건너뜁니다.",
    )


def test_capacity_option_change(smartphones_page: Page):
    scroll_for_lazyload_sync(smartphones_page)
    _assert_option_changes(
        smartphones_page,
        option_selector=CAPACITY_BUTTONS_SELECTOR,
        value_selector=PRICE_TEXT_SELECTOR,
        skip_reason="용량 옵션이 1개 이하여서 변경 검증을 건너뜁니다.",
    )


def test_compare_checkbox_click(smartphones_page: Page):
    scroll_for_lazyload_sync(smartphones_page)

    first_card = _get_first_card_with(smartphones_page, COMPARE_WRAPPER_SELECTOR)
    first_card.scroll_into_view_if_needed()
    expect(first_card).to_be_visible(timeout=CHECK_TIMEOUT)

    compare_label = first_card.locator(COMPARE_WRAPPER_SELECTOR).locator(COMPARE_LABEL_SELECTOR)
    expect(compare_label).to_be_visible(timeout=CHECK_TIMEOUT)

    compare_layer = smartphones_page.locator(COMPARE_LAYER_SELECTOR)
    expect(compare_layer).to_be_hidden(timeout=CHECK_TIMEOUT)

    compare_label.dispatch_event("click")
    smartphones_page.wait_for_timeout(COMPARE_LAYER_WAIT_MS)

    expect(compare_layer).to_be_visible(timeout=CHECK_TIMEOUT)

    layer_class = compare_layer.get_attribute("class") or ""
    assert "open" in layer_class, "비교 레이어가 열리지 않았습니다."
    assert "empty" not in layer_class, "비교 레이어가 아직 비어있습니다."
