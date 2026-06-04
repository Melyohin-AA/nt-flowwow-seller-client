from typing import Any, TypeVar
from ._errors import FwParsingError


T = TypeVar("T")


def _validate_type(name, value: Any, t: type[T]) -> T:
    if isinstance(value, t):
        return value
    raise FwParsingError(name, f"expected {value} to be of type {t} but was of type {type(value)}")


def _read(raw: dict[str, Any], key: str, t: type[T]) -> T:
    value = raw.get(key)
    if value is not None:
        return _validate_type(key, value, t)
    raise FwParsingError(key, "required but omitted")


def _read_opt(raw: dict[str, Any], key: str, t: type[T]) -> T | None:
    value = raw.get(key)
    if value is None:
        return None
    return _validate_type(key, value, t)


def _empty_str_as_none(s: str | None) -> str | None:
    return None if s == "" else s


# Returned objects

TPageItem = TypeVar("TPageItem")

class FwPage[TPageItem]:
    """
    Represents a paged response result.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param total: Total number of items regardless of pagination
    :type total: int
    :param items: List of items on the page; no guarantee on the list's size
    :type items: list[TPageItem]
    """

    def __init__(self, raw: Any, items_label: str, t: type[TPageItem]) -> None:
        self.raw = _validate_type("page", raw, dict)
        self.total = _read(self.raw, "total", int)
        self.items = [
            t(_validate_type("page.items[i]", item, dict))  # type: ignore[call-arg]
            for item in _read(self.raw, items_label, list)
        ]


class FwShop:
    """
    Represents a shop from a response.

    Some of the actual object's fields may be unparsed but stored within the `raw` field.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param shop_id: Shop ID
    :type shop_id: int
    :param name: Shop's name
    :type name: str
    :param status: Shop's status
    :type status: str
    :param is_verified: Whether the shop is verified
    :type is_verified: bool
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.shop_id = _read(raw, "shopId", int)
        self.name = _read(raw, "name", str)
        self.status = _read(raw, "status", str)
        self.is_verified = _read(raw, "isVerified", bool)


class FwProduct:
    """
    Represents a product from a response.

    Some of the actual object's fields may be unparsed but stored within the `raw` field.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param offer_id: Product's offer ID
    :type offer_id: str | None
    :param product_id: Product ID
    :type product_id: int | None
    :param is_active: Whether the product is active
    :type is_active: bool
    :param type: Product's type
    :type type: int
    :param name: Product's name
    :type name: str
    :param available: Product's availability
    :type available: int
    :param stock: Product's quantity in stock
    :type stock: int
    :param price: Product's price
    :type price: str
    :param discount: Product's discount
    :type discount: str
    :param currency_code: Product's currency code
    :type currency_code: str
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.offer_id = _empty_str_as_none(_read_opt(raw, "offerId", str))
        self.product_id = _read_opt(raw, "productId", int)
        self.is_active = _read(raw, "isActive", bool)
        self.type = _read(raw, "type", int)
        self.name = _read(raw, "name", str)
        self.available = _read(raw, "available", int)
        self.stock = _read(raw, "stock", int)
        self.price = _read(raw, "price", str)
        self.discount = _read(raw, "discount", str)
        self.currency_code = _read(raw, "currencyCode", str)


# Partial errors

class FwFlatProductRespErr:
    """Base flat partial product related error"""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.offer_id = _empty_str_as_none(_read_opt(raw, "offerId", str))
        self.product_id = _read_opt(raw, "productId", int)
        self.message = _read(raw, "message", str)


class FwOfferMappingRespErr(FwFlatProductRespErr):
    """Partial product related error of offer mapping"""

    pass


class FwProductActiveRespErr(FwFlatProductRespErr):
    """Partial product related error of product activeness setting"""

    def __init__(self, raw: dict[str, Any]) -> None:
        super().__init__(raw)
        self.is_active = _read_opt(raw, "isActive", bool)


class FwStockUpdatingRespErr(FwFlatProductRespErr):
    """Partial product related error of stock updating"""

    def __init__(self, raw: dict[str, Any]) -> None:
        super().__init__(raw)
        self.stock = _read(raw, "stock", int)
