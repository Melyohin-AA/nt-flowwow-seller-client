import pytest
import nt_flowwow_seller_client._validation as v
from nt_flowwow_seller_client._errors import FwValidationError


@pytest.mark.parametrize(
    "name, value, is_valid",
    [
        ("valid-1", 1, True),
        ("invalid-2", 2, False),
    ]
)
def test_validate(name, value, is_valid):
    def vf(val):
        assert val == value
        return is_valid
    try:
        assert v.validate(name, value, vf) == value
        assert is_valid
    except FwValidationError as err:
        assert not is_valid
        err_msg = str(err)
        assert name in err_msg
        assert str(value) in err_msg


@pytest.mark.parametrize(
    "name, query_list, is_valid",
    [
        ("valid-empty", [], True),
        ("valid", [1, 2, 3], True),
        ("valid-lengthy", [1] * 1000, True),
        ("invalid-item", [1, -1, 3], False),
        ("invalid-lengthy", [1] * 1001, False),
    ]
)
def test_validate_query_list(name, query_list, is_valid):
    validated = []
    def vf(val):
        validated.append(val)
        return val > 0
    try:
        assert v.validate_query_list(name, query_list, vf) == query_list
        assert validated == query_list
        assert is_valid
    except FwValidationError as err:
        assert not is_valid
        err_msg = str(err)
        assert name in err_msg


@pytest.mark.parametrize(
    "token, expected_err_repr",
    [
        ("token", None),
        ("", "<empty>"),
        ("ab" * 2048, "abab<...>abababab"),
        (123, "123"),
    ]
)
def test_validate_token(token, expected_err_repr):
    try:
        assert v.validate_token(token) == token
        assert expected_err_repr is None
    except FwValidationError as err:
        assert expected_err_repr is not None
        assert expected_err_repr in str(err)


@pytest.mark.parametrize(
    "token, is_valid",
    [
        ("a", True), ("a" * 4095, True),
        ("", False), ("a" * 4096, False),
    ]
)
def test_is_token_valid(token, is_valid):
    assert v.is_token_valid(token) == is_valid


@pytest.mark.parametrize(
    "id, is_valid",
    [
        (1, True), ((1 << 32) - 1, True),
        (0, False), (1 << 32, False),
        ("1", False), (True, False),
    ]
)
def test_is_int32_id_valid(id, is_valid):
    assert v.is_int32_id_valid(id) == is_valid


@pytest.mark.parametrize(
    "offer_id, is_valid",
    [
        ("a", True), ("a" * 50, True),
        ("", False), ("a" * 51, False),
    ]
)
def test_is_offer_id_valid(offer_id, is_valid):
    assert v.is_offer_id_valid(offer_id) == is_valid


@pytest.mark.parametrize(
    "stock, is_valid",
    [
        (0, True), ((1 << 32) - 1, True),
        (-1, False), (1 << 32, False),
        ("1", False), (True, False),
    ]
)
def test_is_stock_valid(stock, is_valid):
    assert v.is_stock_valid(stock) == is_valid


@pytest.mark.parametrize(
    "page, is_valid",
    [
        (123, True), (0, True), (-1, False),
        ("1", False), (True, False),
    ]
)
def test_is_page_valid(page, is_valid):
    assert v.is_page_valid(page) == is_valid


@pytest.mark.parametrize(
    "limit, is_valid",
    [
        (1, True), (50, True),
        (0, False), (51, False),
        ("1", False), (True, False),
    ]
)
def test_is_shop_limit_valid(limit, is_valid):
    assert v.is_shop_limit_valid(limit) == is_valid


@pytest.mark.parametrize(
    "limit, is_valid",
    [
        (1, True), (1000, True),
        (0, False), (1001, False),
        ("1", False), (True, False),
    ]
)
def test_is_product_limit_valid(limit, is_valid):
    assert v.is_product_limit_valid(limit) == is_valid


@pytest.mark.parametrize(
    "limit, is_valid",
    [
        (1, True), (100, True),
        (0, False), (101, False),
        ("1", False), (True, False),
    ]
)
def test_is_order_limit_valid(limit, is_valid):
    assert v.is_order_limit_valid(limit) == is_valid


@pytest.mark.parametrize(
    "prod_type, is_valid",
    [
        (1, True), (2, True), (3, True),
        (0, False), (4, False),
        (0.99, False), (3.01, False), (2.5, False),
        ("1", False), (True, False),
    ]
)
def test_is_product_type_valid(prod_type, is_valid):
    assert v.is_product_type_valid(prod_type) == is_valid


def test_is_order_delivery_type_valid():
    assert v.is_order_delivery_type_valid("1") == False
    assert v.is_order_delivery_type_valid(True) == False
    for delivery_type in range(-1, max(v.VALID_ORDER_DELIVERY_TYPES) + 2):
        assert v.is_order_delivery_type_valid(delivery_type) == (delivery_type in v.VALID_ORDER_DELIVERY_TYPES)
        assert v.is_order_delivery_type_valid(delivery_type - 0.1) == False


def test_is_order_status_valid():
    assert v.is_order_status_valid("1") == False
    assert v.is_order_status_valid(True) == False
    for status in range(-1, max(v.VALID_ORDER_STATUSES) + 2):
        assert v.is_order_status_valid(status) == (status in v.VALID_ORDER_STATUSES)
        assert v.is_order_status_valid(status - 0.1) == False


@pytest.mark.parametrize(
    "delivery_time_type, is_valid",
    [
        (0, True), (1, True), (2, True),
        (-1, False), (3, False),
        (0.99, False), (2.01, False), (1.5, False),
        ("1", False), (True, False),
    ]
)
def test_is_order_delivery_time_type_valid(delivery_time_type, is_valid):
    assert v.is_order_delivery_time_type_valid(delivery_time_type) == is_valid
