from utils import scroll_for_lazyload, click_more_button_all
from playwright.async_api import async_playwright, TimeoutError
from config import PRODUCTS_PATH, ROOT, SMARTPHONES_URL
import asyncio
import json
import sys


if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def crawl_html(url: str) -> list[dict] | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(url=url, wait_until="load", timeout=15000)
        except TimeoutError:
            print("TimeoutError")
            await browser.close()
            return None

        await scroll_for_lazyload(page)
        await click_more_button_all(page)

        all_products = []
        
        locator = page.locator("#pfProductCard [id^='li-prd']")
        await locator.first.wait_for()
        items = await locator.all()

        for i, item in enumerate(items):
            prd_name: str | None = None
            prd_code: str | None = None
            rating_point: str = "0"
            review_count: str = "0"
            card_point: str = "0"
            size_list: list[str] = []
            price_won: str = "0"
            btn_text: str | None = None

            try:
                prd_name = (await item.locator(".pf-product-card__name > span").text_content()).strip()
            except Exception:
                print(f"Error (prd_name): {i}")
                continue
            
            try:
                prd_code = (await item.locator(".pf-product-card__prd-code").text_content()).strip()
            except Exception:
                print(f"Error (prd_code): {i}")
                continue
            
            try:
                rating_point = (await item.locator(".rating-point").text_content()).replace("평점", "").strip()
            except Exception:
                print(f"Error (rating_point): {i}")
                continue
            
            try:
                review_count = (await item.locator(".review-count > a").text_content()).replace(",", "").strip()
            except Exception:
                print(f"Error (review_count): {i}")
                continue
            
            try:
                price_won_locator = item.locator(".price-won")
                if await price_won_locator.count() == 0:
                    price_won = "0"
                else:
                    price_text = await price_won_locator.text_content()
                    if price_text.endswith("~"):
                        price_won = price_text.replace("월", "").replace(",", "").replace("원~", "").strip()
                        price_won = str(int(price_won) * 12)
                    else:
                        price_won = price_text.replace(",", "").replace("원", "").strip()
            except Exception:
                print(f"Error (price_won): {i}")
                continue
            
            try:
                if price_won == "0":
                    card_point = "0"
                else:
                    card_point = (await item.locator(".pf-product-card__point-wrap .point").text_content()).replace(",", "").replace("P", "").strip()
            except Exception:
                print(f"Error (card_point): {i}")
                continue

            try:
                size_locator = item.locator(".pf-option-selector__size-text")
                size_list = await size_locator.all_text_contents()
                size_list = [size.strip() for size in size_list]
            except Exception as e:
                print(f"Error (size_list): {i}")
            
            try:
                cta_btn = item.locator(".pf-product-card__cta > button").first
                if await cta_btn.count() > 0:
                    btn_text = await cta_btn.text_content()
                else:
                    btn_text = None
            except Exception:
                print(f"Error (cta_btn): {i}")
                continue

            print(i, prd_name, prd_code, rating_point, review_count, price_won, card_point, size_list, btn_text)
            all_products.append({
                "prd_name": prd_name,
                "prd_code": prd_code,
                "rating_point": rating_point,
                "review_count": review_count,
                "price_won": price_won,
                "card_point": card_point,
                "size_list": size_list,
                "btn_text": btn_text
            })
        
        await browser.close()
        return all_products


def save_json(products: list[dict]) -> None:
    if products:
        PRODUCTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PRODUCTS_PATH, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print(f"Saved json: {PRODUCTS_PATH}")
    else:
        print("No data")


if __name__ == "__main__":
    products = asyncio.run(crawl_html(url=SMARTPHONES_URL))
    save_json(products=products)
