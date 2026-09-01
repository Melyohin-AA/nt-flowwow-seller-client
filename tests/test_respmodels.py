import pytest
from .model_utils import verify_order_items_equal
import nt_flowwow_seller_client._respmodels as m
from nt_flowwow_seller_client._errors import FwParsingError


@pytest.mark.parametrize(
    "name, value, t, expect_err",
    [
        ("name1", 123, int, False),
        ("name2", "str", int, True),
    ]
)
def test_validate_type(name, value, t, expect_err):
    try:
        assert m._validate_type(name, value, t) == value
        assert not expect_err
    except FwParsingError as err:
        assert expect_err
        msg = str(err)
        assert name in msg
        assert str(value) in msg
        assert str(t) in msg
        assert str(type(value)) in msg


@pytest.mark.parametrize(
    "raw, key, t, expect_err",
    [
        ({"a": "123", "b": 345}, "b", int, False),
        ({"a": "123", "b": 345}, "a", int, True),
        ({"a": "123", "b": 345}, "c", int, True),
    ]
)
def test_read(raw, key, t, expect_err):
    try:
        assert m._read(raw, key, t) == raw[key]
        assert not expect_err
    except FwParsingError as err:
        assert expect_err
        msg = str(err)
        assert key in msg


@pytest.mark.parametrize(
    "raw, key, t, expect_err",
    [
        ({"a": "123", "b": 345}, "b", int, False),
        ({"a": "123", "b": 345}, "a", int, True),
        ({"a": "123", "b": 345}, "c", int, False),
    ]
)
def test_read_opt(raw, key, t, expect_err):
    try:
        assert m._read_opt(raw, key, t) == raw.get(key)
        assert not expect_err
    except FwParsingError as err:
        assert expect_err
        msg = str(err)
        assert key in msg


@pytest.mark.parametrize(
    "s, expected",
    [
        (None, None),
        ("", None),
        ("s", "s"),
    ]
)
def test_empty_str_as_none(s, expected):
    assert m._empty_str_as_none(s) == expected


def test_make_page():
    ITEMS_LABEL = "elems"
    TOTAL = 150
    raw = {ITEMS_LABEL: [{"a": 1}, {"b": 2}], "total": TOTAL}
    page = m.FwPage(dict(raw), ITEMS_LABEL, str)
    assert page.raw == raw
    assert page.total == TOTAL
    assert page.items == ["{'a': 1}", "{'b': 2}"]


def test_make_shop():
    SHOP_ID = 984598
    NAME = "sfjnsf"
    STATUS = "moderation"
    IS_VERIFIED = False
    raw = {"shopId": SHOP_ID, "name": NAME, "status": STATUS, "isVerified": IS_VERIFIED}
    shop = m.FwShop(dict(raw))
    assert shop.raw == raw
    assert shop.shop_id == SHOP_ID
    assert shop.name == NAME
    assert shop.status == STATUS
    assert shop.is_verified == IS_VERIFIED


def test_make_product():
    OFFER_ID = "8738"
    PRODUCT_ID = 9823487
    IS_ACTIVE = False
    TYPE = 3
    NAME = "iusfu"
    AVAILABLE = 64
    STOCK = 12
    PRICE = "123.45"
    DISCOUNT = "0.01"
    CURR = "MNT"
    raw = {
      "offerId": OFFER_ID, "productId": PRODUCT_ID,
      "isActive": IS_ACTIVE, "type": TYPE, "name": NAME,
      "available": AVAILABLE, "stock": STOCK,
      "price": PRICE, "discount": DISCOUNT, "currencyCode": CURR,
    }
    product = m.FwProduct(dict(raw))
    assert product.raw == raw
    assert product.offer_id == OFFER_ID
    assert product.product_id == PRODUCT_ID
    assert product.is_active == IS_ACTIVE
    assert product.type == TYPE
    assert product.name == NAME
    assert product.available == AVAILABLE
    assert product.stock == STOCK
    assert product.price == PRICE
    assert product.discount == DISCOUNT
    assert product.currency_code == CURR


def test_make_order_item():
    OFFER_ID = "4182"
    PRODUCT_ID = 83418243
    COUNT = 2
    COST = "119.80"
    raw = {
        "offerId": OFFER_ID, "productId": PRODUCT_ID,
        "isActive": True, "type": 1, "categoryId": 54, "subCategoryId": 112, "name": "Rose bouquet",
        "description": "Beautiful bouquet of roses", "url": "https://flowwow.com/product/83418243",
        "available": 1, "stock": 10, "minOrder": 1, "price": "59.90", "discount": "20", "currencyCode": "GEL",
        "images": ["https://example.com"], "productionTime": 1, "shipmentTime": 1, "canRent": 1,
        "originalId": 7123456, "isDeliveryPost": True, "isStarred": True, "vat": "10",
        "count": COUNT, "cost": COST
    }
    order_item = m.FwOrderItem(raw)
    assert order_item.raw == raw
    assert order_item.offer_id == OFFER_ID
    assert order_item.product_id == PRODUCT_ID
    assert order_item.count == COUNT
    assert order_item.cost == COST


def test_make_order():
    ID = 19522730
    CREATED_DATE = 1762686732
    STATUS = 1
    DELIVERY_TYPE = 1
    DELIVERY_TIME_TYPE = 2
    SHOP_ADDITIONAL_INFO = "this is a shop comment"
    COMMENT = "this is a client's comment"
    MESSAGE = "this is a card's message"
    USER_NAME = "Ivan Petrov"
    RECIPIENT_NAME = "Marin Tatiani"
    expected_order_item = m.FwOrderItem({
        "offerId": "4182", "productId": 83418243,
        "isActive": True, "type": 1, "categoryId": 54, "subCategoryId": 112, "name": "Rose bouquet",
        "description": "Beautiful bouquet of roses", "url": "https://flowwow.com/product/83418243",
        "available": 1, "stock": 10, "minOrder": 1, "price": "59.90", "discount": "20", "currencyCode": "GEL",
        "images": ["https://example.com"], "productionTime": 1, "shipmentTime": 1, "canRent": 1,
        "originalId": 7123456, "isDeliveryPost": True, "isStarred": True, "vat": "10",
        "count": 2, "cost": "119.80"
    })
    raw = {
        "id": ID, "shopId": 260, "createdDate": CREATED_DATE,
        "status": STATUS, "deliveryType": DELIVERY_TYPE, "deliveryTimeType": DELIVERY_TIME_TYPE,
        "deliveryDateFrom": 1762686732, "deliveryDateTo": 1762686732,
        "address": "123 Pekini street", "courierInfo": "entrance door code is 5547",
        "shopAdditionalInfo": SHOP_ADDITIONAL_INFO, "comment": COMMENT,
        "photoBeforeUrl": "https://flowwow.com/data/flowphoto_before/150/8e/68b5ae8c5ma8e.jpg",
        "photoAfterUrl": "https://flowwow.com/data/flowphoto_before/150/6e/69a5ae129cd7d.jpg",
        "message": MESSAGE, "products": [expected_order_item.raw],
        "user": {"name": USER_NAME, "phone": "+7991234567"},
        "recipient": {"name": RECIPIENT_NAME, "phone": "+995987654321"},
        "sourceHost": None
    }
    order = m.FwOrder(raw)
    assert raw == order.raw
    assert ID == order.id
    assert CREATED_DATE == order.created_date
    assert STATUS == order.status
    assert DELIVERY_TYPE == order.delivery_type
    assert DELIVERY_TIME_TYPE == order.delivery_time_type
    assert SHOP_ADDITIONAL_INFO == order.shop_additional_info
    assert COMMENT == order.comment
    assert MESSAGE == order.message
    assert USER_NAME == order.user_name
    assert RECIPIENT_NAME == order.recipient_name
    assert len(order.products) == 1
    verify_order_items_equal(expected_order_item, order.products[0])


def test_make_flat_product_error():
    OFFER_ID = "8738"
    PRODUCT_ID = 9823487
    MESSAGE = "everything is wrong!!"
    raw = {"offerId": OFFER_ID, "productId": PRODUCT_ID, "message": MESSAGE}
    err = m.FwFlatProductRespErr(dict(raw))
    assert err.raw == raw
    assert err.offer_id == OFFER_ID
    assert err.product_id == PRODUCT_ID
    assert err.message == MESSAGE
