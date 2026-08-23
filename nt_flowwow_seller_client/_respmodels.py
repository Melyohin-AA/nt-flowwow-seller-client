from typing import Any, TypeVar, Generic
from ._errors import FwParsingError


T = TypeVar("T")


def _validate_type(name, value: Any, t: type[T]) -> T:
    if type(value) is t:
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

class FwPage(Generic[TPageItem]):
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


class FwOrderItem:
    """
    Represents an ordered product from a response.

    Some of the actual object's fields may be unparsed but stored within the `raw` field.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param offer_id: Ordered Product's offer ID
    :type offer_id: str | None
    :param product_id: Ordered Product's product ID
    :type product_id: int | None
    :param count: Ordered Product's number
    :type count: int
    :param cost: Ordered Product's cost //~ specify if it is a cost per unit or an overall cost
    :type cost: str
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.offer_id = _empty_str_as_none(_read_opt(raw, "offerId", str))
        self.product_id = _read_opt(raw, "productId", int)
        self.count = _read(raw, "count", int)
        self.cost = _read(raw, "cost", str)


class FwOrder:
    """
    Represents an order from a response.

    Some of the actual object's fields may be unparsed but stored within the `raw` field.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param id: Order ID
    :type id: int | None
    :param created_date: Order's creation UNIX timestamp in seconds
    :type created_date: int | None
    :param status: Order's status
    :type status: int | None
    :param delivery_type: Order's delivery type
    :type delivery_type: int | None
    :param courier_info: A comment for a courier
    :type courier_info: str | None
    :param shop_additional_info: A comment for a shop
    :type shop_additional_info: str | None
    :param comment: Customer's comment
    :type comment: str | None
    :param message: Postcard text
    :type message: str | None
    :param user_name: Customer's name
    :type user_name: str | None
    :param recipient_name: Recipient's name
    :type recipient_name: str | None
    :param products: Order's items
    :type products: list[FwOrderItem] | None
    """

    def __init__(self, raw: Any) -> None:
        self.raw = _validate_type("order", raw, dict)
        self.id = _read_opt(raw, "id", int)
        self.created_date = _read_opt(raw, "createdDate", int)
        self.status = _read_opt(raw, "status", int)
        self.delivery_type = _read_opt(raw, "deliveryType", int)
        self.courier_info = _read_opt(raw, "courierInfo", str)
        self.shop_additional_info = _read_opt(raw, "shopAdditionalInfo", str)
        self.comment = _read_opt(raw, "comment", str)
        self.message = _read_opt(raw, "message", str)
        user = _read_opt(raw, "user", dict)
        self.user_name = _read(user, "name", str) if user else None
        recipient = _read_opt(raw, "recipient", dict)
        self.recipient_name = _read(recipient, "name", str) if recipient else None
        self.products = (
            [FwOrderItem(_validate_type("products[i]", p, dict)) for p in products]
            if (products := _read_opt(raw, "products", list)) else
            None
        )


# Partial errors

class FwFlatProductRespErr:
    """
    Base flat partial product-related error.

    :param raw: Raw JSON-compatible value
    :type raw: dict[str, Any]
    :param offer_id: Product's offer ID
    :type offer_id: str | None
    :param product_id: Product ID
    :type product_id: int | None
    :param message: Error message
    :type message: str
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.offer_id = _empty_str_as_none(_read_opt(raw, "offerId", str))
        self.product_id = _read_opt(raw, "productId", int)
        self.message = _read(raw, "message", str)


class FwOfferMappingRespErr(FwFlatProductRespErr):
    """Partial product related error of offer mapping"""


class FwProductActiveRespErr(FwFlatProductRespErr):
    """
    Partial product related error of product activeness setting.

    :param is_active: Whether the product is active
    :type is_active: bool | None
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        super().__init__(raw)
        self.is_active = _read_opt(raw, "isActive", bool)


class FwStockUpdatingRespErr(FwFlatProductRespErr):
    """
    Partial product related error of stock updating.

    :param stock: Product's quantity in stock
    :type stock: int
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        super().__init__(raw)
        self.stock = _read(raw, "stock", int)
