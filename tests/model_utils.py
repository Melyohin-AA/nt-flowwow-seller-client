from typing import Any, Callable, TypeVar
import nt_flowwow_seller_client._respmodels as _respmodels


def make_shop_page(raw_page: dict[str, Any]) -> _respmodels.FwPage[_respmodels.FwShop]:
    return _respmodels.FwPage(raw_page, "shops", _respmodels.FwShop)


def make_product_page(raw_page: dict[str, Any]) -> _respmodels.FwPage[_respmodels.FwProduct]:
    return _respmodels.FwPage(raw_page, "items", _respmodels.FwProduct)


T = TypeVar("T")

def verify_pages_equal(e: _respmodels.FwPage[T], a: _respmodels.FwPage[T], vf: Callable[[T, T], None]) -> None:
    assert e.raw == a.raw
    assert e.total == a.total
    assert len(e.items) == len(a.items)
    for a_item, b_item in zip(e.items, a.items):
        vf(a_item, b_item)


def verify_shops_equal(e: _respmodels.FwShop, a: _respmodels.FwShop) -> None:
    assert e.raw == a.raw
    assert e.shop_id == a.shop_id
    assert e.name == a.name
    assert e.status == a.status
    assert e.is_verified == a.is_verified


def verify_products_equal(e: _respmodels.FwProduct, a: _respmodels.FwProduct) -> None:
    assert e.raw == a.raw
    assert e.offer_id == a.offer_id
    assert e.product_id == a.product_id
    assert e.is_active == a.is_active
    assert e.type == a.type
    assert e.name == a.name
    assert e.available == a.available
    assert e.stock == a.stock
    assert e.price == a.price
    assert e.discount == a.discount
    assert e.currency_code == a.currency_code


def _verify_flat_product_errors_equal(e: _respmodels.FwFlatProductRespErr, a: _respmodels.FwFlatProductRespErr) -> None:
    assert e.raw == a.raw
    assert e.offer_id == a.offer_id
    assert e.product_id == a.product_id
    assert e.message == a.message


def verify_offer_mapping_errors_equal(
    e_list: list[_respmodels.FwOfferMappingRespErr], a_list: list[_respmodels.FwOfferMappingRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)


def verify_product_activeness_errors_equal(
    e_list: list[_respmodels.FwProductActiveRespErr], a_list: list[_respmodels.FwProductActiveRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)
        assert e.is_active == a.is_active


def verify_stock_updating_errors_equal(
    e_list: list[_respmodels.FwStockUpdatingRespErr], a_list: list[_respmodels.FwStockUpdatingRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)
        assert e.stock == a.stock
