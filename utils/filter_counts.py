SIZE_FILTER_KEYS = ["128 GB", "256 GB", "512 GB", "1 TB"]


def normalize_size(size: str) -> str:
    return size.replace(" ", "")


def combination_label(filter_keys: list[str], state: int) -> str:
    n = len(filter_keys)
    selected = [filter_keys[i] for i in range(n) if (state >> (n - 1 - i)) & 1]
    return " + ".join(selected) if selected else "(none)"


def build_size_counter(
    products: list[dict], filter_keys: list[str] | None = None
) -> dict[int, int]:
    """단일 용량 필터의 모든 bitmask 조합(2^n)에 대한 기대 상품 수."""
    if filter_keys is None:
        filter_keys = SIZE_FILTER_KEYS

    n = len(filter_keys)
    counter: dict[int, int] = {}

    for state in range(2**n):
        if state == 0:
            counter[state] = len(products)
            continue

        count = 0
        selected = {
            normalize_size(filter_keys[i])
            for i in range(n)
            if (state >> (n - 1 - i)) & 1
        }

        for product in products:
            sizes = product.get("size_list", [])
            if not sizes:
                continue

            product_sizes = {normalize_size(size) for size in sizes}
            if product_sizes & selected:
                count += 1

        counter[state] = count

    return counter
