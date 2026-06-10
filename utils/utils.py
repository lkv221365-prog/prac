from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage
import asyncio
import logging
import time


log = logging.getLogger(__name__)


async def scroll_for_lazyload(page: AsyncPage) -> None:
    """
    페이지의 모든 컨텐츠가 로드될 수 있도록 점진적으로 스크롤합니다.
    쿠키 동의 버튼 클릭으로 인한 페이지 리다이렉트가 발생해도 안전하게 스크롤을 계속합니다.
    """
    log.debug("Starting scroll operation for lazy-loaded content")
    try:
        viewport_height = await page.evaluate("window.innerHeight")
        page_height = await page.evaluate("document.body.scrollHeight")
        log.debug(f"Viewport height: {viewport_height}px, Total page height: {page_height}px")
        scroll_step = int(viewport_height * 0.8)
        log.debug(f"Scroll step: {scroll_step}px")
        current_position = 0
        consent_button_clicked = False

        while True:
            try:
                # 현재 페이지 높이 확인
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_position >= current_height:
                    break

                # 스크롤 수행
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                log.debug(f"Scrolled to position: {current_position}px / {current_height}px")
                current_position += scroll_step
                await asyncio.sleep(1.0)

                # 쿠키 동의 버튼 처리
                if not consent_button_clicked:
                    try:
                        button_exists = await page.evaluate("""
                            () => {
                                const button = document.querySelector('#truste-consent-button');
                                if (button && button.offsetParent !== null) {
                                    button.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        if button_exists:
                            consent_button_clicked = True
                            log.info("Cookie consent button clicked")
                            await asyncio.sleep(2.0)  # 쿠키 동의 후 페이지가 안정화될 때까지 대기
                    except Exception as e:
                        log.error(f"Error handling cookie consent button: {e}")

            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    # 페이지가 리다이렉트되었지만, 현재 위치를 유지하고 계속 진행
                    log.info("Page reloaded, continuing scroll from current position")
                    await asyncio.sleep(2.0)  # 페이지 로드 대기
                    continue
                raise

        # 스크롤 완료 후 정리
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        log.debug("Scrolled back to top of page")

    except Exception as e:
        log.error(f"Error during page scrolling: {e}", exc_info=True)


def scroll_for_lazyload_sync(page: SyncPage) -> None:
    """
    sync API용 lazy-load 스크롤. scroll_for_lazyload와 동일한 동작을 수행합니다.
    """
    log.debug("Starting scroll operation for lazy-loaded content")
    try:
        viewport_height = page.evaluate("window.innerHeight")
        page.evaluate("document.body.scrollHeight")
        log.debug(f"Viewport height: {viewport_height}px")
        scroll_step = int(viewport_height * 0.8)
        log.debug(f"Scroll step: {scroll_step}px")
        current_position = 0
        consent_button_clicked = False

        while True:
            try:
                current_height = page.evaluate("document.body.scrollHeight")
                if current_position >= current_height:
                    break

                page.evaluate(f"window.scrollTo(0, {current_position})")
                log.debug(f"Scrolled to position: {current_position}px / {current_height}px")
                current_position += scroll_step
                time.sleep(1.0)

                if not consent_button_clicked:
                    try:
                        button_exists = page.evaluate("""
                            () => {
                                const button = document.querySelector('#truste-consent-button');
                                if (button && button.offsetParent !== null) {
                                    button.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        if button_exists:
                            consent_button_clicked = True
                            log.info("Cookie consent button clicked")
                            time.sleep(2.0)
                    except Exception as e:
                        log.error(f"Error handling cookie consent button: {e}")

            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    log.info("Page reloaded, continuing scroll from current position")
                    time.sleep(2.0)
                    continue
                raise

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        log.debug("Scrolled back to top of page")

    except Exception as e:
        log.error(f"Error during page scrolling: {e}", exc_info=True)


async def click_more_button_all(page: AsyncPage) -> None:
    more_button = page.locator("#morePrd")
    while True:
        if await more_button.is_disabled():
            break        
        await more_button.click()
        print("More button clicked")
        await asyncio.sleep(0.5)
