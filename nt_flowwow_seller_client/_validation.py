from typing import Any, Callable, TypeVar
from ._errors import FwValidationError


T = TypeVar("T")


def validate(name: str, value: T, vf: Callable[[Any], bool]) -> T:
    if vf(value):
        return value
    raise FwValidationError(name, value)


def validate_query_list(name: str, query_list: list[T], vf: Callable[[Any], bool]) -> list[T]:
    if (type(query_list) is list) and (len(query_list) <= 1000) and all(vf(item) for item in query_list):
        return query_list
    raise FwValidationError(name, query_list)


def validate_token(token: Any) -> str:
    if is_token_valid(token):
        return token
    if isinstance(token, str):
        value = f"{token[:4]}<...>{token[-8:]}" if token else "<empty>"
    else:
        value = token
    raise FwValidationError("token", value)


def is_token_valid(token: Any) -> bool:
    return (type(token) is str) and (0 < len(token) < 4096)


def is_int32_valid(id: Any) -> bool:
    return (type(id) is int) and (0 <= id <= 0xFFFF_FFFF)


def is_int32_id_valid(id: Any) -> bool:
    return (type(id) is int) and (0 < id <= 0xFFFF_FFFF)


def is_offer_id_valid(offer_id: Any) -> bool:
    return (type(offer_id) is str) and (0 < len(offer_id) <= 50)


def is_stock_valid(stock: Any) -> bool:
    return (type(stock) is int) and (0 <= stock <= 0xFFFF_FFFF)


def is_page_valid(page: Any) -> bool:
    return (type(page) is int) and (page >= 0)


def is_shop_limit_valid(limit: Any) -> bool:
    return (type(limit) is int) and (0 < limit <= 50)


def is_product_limit_valid(limit: Any) -> bool:
    return (type(limit) is int) and (0 < limit <= 1000)


def is_order_limit_valid(limit: Any) -> bool:
    return (type(limit) is int) and (0 < limit <= 100)


def is_product_type_valid(prod_type: Any) -> bool:
    return (type(prod_type) is int) and (1 <= prod_type <= 3)
