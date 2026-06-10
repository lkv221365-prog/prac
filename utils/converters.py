def as_int(value) -> int:
    if value is None or value == "":
        return 0
    return int(value)


def as_float(value) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)
