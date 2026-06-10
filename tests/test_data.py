from utils import as_float, as_int
import math


def test_all_product_codes_are_unique(open_json):
    prd_codes = [p["prd_code"] for p in open_json]
    unique_codes = set(prd_codes)

    assert len(unique_codes) == len(prd_codes)


def test_product_business_rules(product: dict):
    name = product["prd_name"]
    price = as_int(product["price_won"])
    card_point = as_int(product["card_point"])

    rating_point = as_float(product["rating_point"])
    review_count = as_int(product["review_count"])

    assert rating_point >= 0 and rating_point <= 5, f"{name}: 평점은 0~5 사이여야 합니다"
    assert review_count >= 0, f"{name}: 리뷰수는 0 이상이어야 합니다"
    if review_count == 0:
        assert rating_point == 0, f"{name}: 리뷰수가 0인경우 평점도 0이어야 합니다"

    if price == 0:
        assert card_point == 0, f"{name}: 가격 0원일 때 card_point는 0이어야 합니다"
        assert product["btn_text"] == "제품 정보 보기", f"{name}: 가격 0원일 때 btn_text 불일치"
        return

    if "자급제" in name:
        assert product["btn_text"] == "구매하기", f"{name}: 자급제 상품 btn_text 불일치"

        expected_point = math.floor(price / 1000)
        assert card_point == expected_point, (
            f"{name}: card_point {card_point} != {expected_point}"
        )

    if "통신사폰" in name:
        assert product["btn_text"] == "신청하기", f"{name}: 통신사폰 btn_text 불일치"

    
