from urllib.parse import urlparse
from playwright.sync_api import Page, expect, sync_playwright
from config import GNB_URLS_PATH, NAV_TIMEOUT, PAGE_LOAD_WAIT_MS, SMARTPHONES_URL
import json
import re

GNB_ROOT_SELECTOR = ".nv00-gnb-v4"
GNB_L0_LINK_SELECTOR = f"{GNB_ROOT_SELECTOR} .nv00-gnb-v4__l0-menu-link"
GNB_LINK_SELECTOR = f"{GNB_ROOT_SELECTOR} a[onclick*='openCtaLink']"
URL_REGEX = re.compile(r"openCtaLink\(\s*['\"]([^'\"]+)['\"]")
VIEWPORT = {"width": 1920, "height": 1080}


def _parse_open_cta_url(onclick_text: str) -> str | None:
    match = URL_REGEX.search(onclick_text)
    if not match:
        return None
    return match.group(1)


def _dismiss_cookie_consent(page: Page) -> None:
    try:
        clicked = page.evaluate(
            """
            () => {
                const button = document.querySelector('#truste-consent-button');
                if (button && button.offsetParent !== null) {
                    button.click();
                    return true;
                }
                return false;
            }
            """
        )
        if clicked:
            print("[INFO] 쿠키 동의 버튼 클릭")
            page.wait_for_timeout(2000)
    except Exception as exc:
        print(f"[WARN] 쿠키 동의 처리 실패: {exc}")


def _prepare_gnb_page(page: Page) -> None:
    print(f"[INFO] GNB 루트 대기 (selector: {GNB_ROOT_SELECTOR})")
    gnb_root = page.locator(GNB_ROOT_SELECTOR).first
    expect(gnb_root).to_be_attached(timeout=10000)
    _dismiss_cookie_consent(page)


def _reveal_gnb_menus(page: Page) -> None:
    l0_links = page.locator(GNB_L0_LINK_SELECTOR)
    l0_count = l0_links.count()
    print(f"[INFO] L0 GNB 메뉴 hover 시작 ({l0_count}개)")

    for i in range(l0_count):
        link = l0_links.nth(i)
        label = (link.text_content() or "").strip() or f"menu-{i}"
        try:
            link.hover(timeout=3000)
            page.wait_for_timeout(400)
            print(f"[INFO] L0 hover 완료: {label}")
        except Exception as exc:
            print(f"[WARN] L0 hover 실패 ({label}): {exc}")


def _extract_urls_with_locator(page: Page) -> set[str]:
    print(f"[INFO] locator 추출 시작 (selector: {GNB_LINK_SELECTOR})")
    gnb_links = page.locator(GNB_LINK_SELECTOR)
    total_link_elements = gnb_links.count()
    print(f"[INFO] DOM에서 발견한 GNB 링크 요소 수: {total_link_elements}")

    extracted_urls: set[str] = set()
    skipped_no_onclick = 0
    skipped_no_match = 0
    skipped_not_http = 0

    for i in range(total_link_elements):
        onclick_text = gnb_links.nth(i).get_attribute("onclick")
        if not onclick_text:
            skipped_no_onclick += 1
            continue

        parsed_url = _parse_open_cta_url(onclick_text)
        if not parsed_url:
            skipped_no_match += 1
            continue

        if parsed_url.startswith("http"):
            extracted_urls.add(parsed_url)
        else:
            skipped_not_http += 1

    print(
        "[INFO] locator 추출 요약 - "
        f"고유 URL: {len(extracted_urls)}, "
        f"onclick 없음: {skipped_no_onclick}, "
        f"패턴 불일치: {skipped_no_match}, "
        f"http 아님: {skipped_not_http}"
    )
    return extracted_urls


def _extract_urls_with_js(page: Page) -> set[str]:
    print("[INFO] JS DOM 스캔 fallback 시작")
    urls: list[str] = page.evaluate(
        """
        () => {
            const urls = new Set();
            const pattern = /openCtaLink\\(\\s*['"]([^'"]+)['"]/;
            document.querySelectorAll("a[onclick*='openCtaLink']").forEach((anchor) => {
                const onclick = anchor.getAttribute("onclick") || "";
                const match = onclick.match(pattern);
                if (match && match[1].startsWith("http")) {
                    urls.add(match[1]);
                }
            });
            return [...urls].sort();
        }
        """
    )
    print(f"[INFO] JS DOM 스캔 결과: {len(urls)}개 URL")
    return set(urls)


def extract_gnb_urls_from_page(page: Page) -> list[str]:
    _prepare_gnb_page(page)
    _reveal_gnb_menus(page)

    extracted_urls = _extract_urls_with_locator(page)
    if not extracted_urls:
        extracted_urls = _extract_urls_with_js(page)

    for index, url in enumerate(sorted(extracted_urls), start=1):
        print(f"[EXTRACT] {index}: {url}")

    print(f"[INFO] 최종 고유 URL 수: {len(extracted_urls)}")
    return sorted(extracted_urls)


def load_gnb_urls() -> list[str]:
    if not GNB_URLS_PATH.exists():
        return []
    with open(GNB_URLS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_gnb_urls(urls: list[str]) -> None:
    sorted_urls = sorted(set(urls))
    print(f"[INFO] JSON 저장 시작: {GNB_URLS_PATH}")
    GNB_URLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GNB_URLS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_urls, f, ensure_ascii=False, indent=2)
    print(f"[INFO] JSON 저장 완료 ({len(sorted_urls)}개 URL)")


def url_test_id(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_") or "root"
    return path[:80]


def extract_and_save_gnb_urls(*, headed: bool = False) -> list[str]:
    print("[START] GNB URL 추출 및 저장 프로세스 시작")
    print(f"[INFO] 브라우저 모드: {'headed' if headed else 'headless'}")
    print(f"[INFO] 시작 URL: {SMARTPHONES_URL}")

    with sync_playwright() as playwright:
        print("[INFO] Chromium 브라우저 실행")
        browser = playwright.chromium.launch(headless=not headed)
        page = browser.new_page(locale="ko-KR", viewport=VIEWPORT)
        print("[INFO] 페이지 이동 중...")
        page.goto(SMARTPHONES_URL, wait_until="load", timeout=NAV_TIMEOUT)
        print("[INFO] 페이지 로드 완료, 3초 대기")
        page.wait_for_timeout(PAGE_LOAD_WAIT_MS)

        urls = extract_gnb_urls_from_page(page)
        if not urls:
            print("[ERROR] 추출된 URL이 없습니다. GNB 구조 또는 선택자를 확인하세요.")
        save_gnb_urls(urls)
        print("[INFO] 브라우저 종료")
        browser.close()

    print(f"[DONE] 총 {len(urls)}개 URL을 {GNB_URLS_PATH}에 저장했습니다.")
    return urls


if __name__ == "__main__":
    extract_and_save_gnb_urls()
