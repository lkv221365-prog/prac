from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright
from dotenv import load_dotenv
from config import (
    ENV_PATH,
    NAV_TIMEOUT,
    PAGE_LOAD_WAIT_MS,
    PRODUCTS_PATH,
    SLACK_WEBHOOK_ENV_VAR,
    SMARTPHONES_URL,
)
import os
import json
import pytest
import urllib.error
import urllib.request

load_dotenv(ENV_PATH)


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Playwright browser in headed (visible) mode",
    )
    parser.addoption(
        "--no-slack-report",
        action="store_true",
        default=False,
        help="Skip Slack test summary notification",
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, request) -> Browser:
    headed = request.config.getoption("--headed")
    browser = playwright_instance.chromium.launch(headless=not headed)
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    ctx = browser.new_context(locale="ko-KR")
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def smartphones_page(page: Page) -> Page:
    page.goto(SMARTPHONES_URL, wait_until="load", timeout=NAV_TIMEOUT)
    page.wait_for_timeout(PAGE_LOAD_WAIT_MS)
    return page


def load_products() -> list[dict]:
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def open_json() -> list[dict]:
    return load_products()


def pytest_generate_tests(metafunc):
    if "product" in metafunc.fixturenames:
        products = load_products()
        metafunc.parametrize(
            "product",
            products,
            ids=[f"상품 검증: {p['prd_name']}" for p in products],
        )


def _get_slack_webhook_url() -> str:
    return os.environ.get(SLACK_WEBHOOK_ENV_VAR, "").strip()


def _send_slack_report(terminalreporter, exitstatus: int, webhook_url: str) -> None:
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    errors = len(terminalreporter.stats.get("error", []))
    total = passed + failed + skipped + errors

    if exitstatus == 0:
        title = "🟢 테스트 자동화 결과: 모든 테스트 통과!"
        color = "#2EB67D"
    else:
        title = "🔴 테스트 자동화 결과: 일부 테스트 실패 발생"
        color = "#E01E5A"

    failed_reports = terminalreporter.stats.get("failed", [])
    error_reports = terminalreporter.stats.get("error", [])
    issue_reports = failed_reports + error_reports

    failed_details = ""
    if issue_reports:
        failed_details = "\n*❌ 실패한 테스트 목록:*\n"
        for rep in issue_reports[:5]:
            failed_details += f"• `{rep.nodeid.split('::')[-1]}`\n"
        if len(issue_reports) > 5:
            failed_details += f"• 외 {len(issue_reports) - 5}개 더 실패함...\n"

    summary_text = (
        f"*{title}*\n"
        f"• *총 테스트 개수:* {total}개\n"
        f"• *통과:* {passed}개  |  *실패:* {failed}개  |  "
        f"*스킵:* {skipped}개  |  *에러:* {errors}개"
    )

    slack_payload = {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": summary_text},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": failed_details or "모든 테스트가 정상적으로 완료되었습니다.",
                        },
                    },
                ],
            }
        ]
    }

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(slack_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                print(f"[ERROR] Slack 전송 실패: HTTP {response.status}")
            else:
                print("[INFO] Slack 테스트 결과 리포트 전송 완료")
    except urllib.error.URLError as exc:
        print(f"[ERROR] Slack 통신 중 에러 발생: {exc}")
    except Exception as exc:
        print(f"[ERROR] Slack 통신 중 에러 발생: {exc}")


def _slack_skip_reason(config) -> str | None:
    if config.getoption("--no-slack-report"):
        return "--no-slack-report 옵션으로 비활성화됨"
    webhook_url = _get_slack_webhook_url()
    if not webhook_url:
        return f"{SLACK_WEBHOOK_ENV_VAR} 환경 변수(또는 .env)가 설정되지 않음"
    if not webhook_url.startswith("https://hooks.slack.com/"):
        return f"{SLACK_WEBHOOK_ENV_VAR} 형식이 올바르지 않음 (hooks.slack.com 으로 시작해야 함)"
    return None


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    skip_reason = _slack_skip_reason(config)
    if skip_reason:
        print(f"[INFO] Slack 리포트 스킵: {skip_reason}")
        return
    _send_slack_report(terminalreporter, exitstatus, _get_slack_webhook_url())
