def test_intentional_success_for_log_check():
    """테스트 성공."""
    assert True, "의도적인 성공: 로그 확인용 테스트"


def test_intentional_failure_for_log_check():
    """테스트 실패."""
    assert False, "의도적인 실패: 로그 확인용 테스트"


def test_failure_raises_runtime_error():
    """예외 발생 실패 — traceback에 raise 지점이 포함되는지 확인."""
    product = {"prd_name": "갤럭시 S26", "price_won": None}
    if product["price_won"] is None:
        raise RuntimeError(
            f"가격 파싱 실패: {product['prd_name']} — price_won 필드가 비어 있습니다"
        )


def test_failure_filter_count_mismatch():
    """데이터 검증 실패 — 여러 줄 assertion 메시지가 로그에 포함되는지 확인."""
    expected_count = 32
    actual_count = 28
    assert actual_count == expected_count, (
        "필터 결과 수 불일치\n"
        f"  expected: {expected_count}\n"
        f"  actual:   {actual_count}\n"
        "  hint: products.json 갱신 후 MULTI_FILTER_CASES 기대값을 확인하세요"
    )


def test_failure_key_error():
    """KeyError 실패 — 누락된 키 접근 traceback 확인."""
    payload = {"status": "ok", "count": 3}
    _ = payload["error_message"]


def test_failure_nested_call_stack():
    """중첩 호출 실패 — traceback에 여러 프레임이 쌓이는지 확인."""

    def parse_count(raw: str) -> int:
        return int(raw.strip())

    def load_total(raw_values: list[str]) -> int:
        return sum(parse_count(value) for value in raw_values)

    load_total(["10", "20", "not-a-number"])
