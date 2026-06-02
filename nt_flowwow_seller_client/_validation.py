from typing import Any, Callable, TypeVar
from .errors import FwValidationError


T = TypeVar("T")


def validate(name: str, value: T, vf: Callable[[Any], bool]) -> T:
    if vf(value):
        return value
    raise FwValidationError(name, value)


def validate_query_list(name: str, query_list: list[T], vf: Callable[[Any], bool]) -> list[T]:
    if isinstance(query_list, list) and (len(query_list) <= 1000) and all(vf(item) for item in query_list):
        return query_list
    raise FwValidationError(name, query_list)


def is_token_valid(token: Any) -> bool:
    return isinstance(token, str) and (0 < len(token) < 4096)


def is_int32_id_valid(id: Any) -> bool:
    return isinstance(id, int) and (0 < id <= 0xFFFF_FFFF)


def is_offer_id_valid(offer_id: Any) -> bool:
    return isinstance(offer_id, str) and (0 < len(offer_id) <= 50)


def is_stock_valid(stock: Any) -> bool:
    return isinstance(stock, int) and (0 <= stock <= 0xFFFF_FFFF)


def is_page_valid(page: Any) -> bool:
    return isinstance(page, int) and (page >= 0)


def is_shop_limit_valid(limit: Any) -> bool:
    return isinstance(limit, int) and (0 < limit <= 50)


def is_product_limit_valid(limit: Any) -> bool:
    return isinstance(limit, int) and (0 < limit <= 1000)


def is_product_type_valid(type: Any) -> bool:
    return isinstance(type, int) and (1 <= type <= 3)
