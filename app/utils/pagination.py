from typing import Tuple

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def get_pagination_params(page: int | None, page_size: int | None) -> Tuple[int, int]:
    """
    Normalize pagination params and enforce limits.
    Returns (offset, limit).
    """
    p = page or DEFAULT_PAGE
    ps = page_size or DEFAULT_PAGE_SIZE

    if p < 1:
        p = DEFAULT_PAGE
    if ps < 1:
        ps = DEFAULT_PAGE_SIZE
    if ps > MAX_PAGE_SIZE:
        ps = MAX_PAGE_SIZE

    offset = (p - 1) * ps
    limit = ps
    return offset, limit
