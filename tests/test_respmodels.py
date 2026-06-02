import pytest
import nt_flowwow_seller_client.respmodels as m
from nt_flowwow_seller_client.errors import FwParsingError


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


def test_make_flat_product_error():
    OFFER_ID = "8738"
    PRODUCT_ID = 9823487
    MESSAGE = "everything is wrong!!"
    raw = {"offerId": OFFER_ID, "productId": PRODUCT_ID, "message": MESSAGE}
    err = m.FwFlatProductError(dict(raw))
    assert err.raw == raw
    assert err.offer_id == OFFER_ID
    assert err.product_id == PRODUCT_ID
    assert err.message == MESSAGE
