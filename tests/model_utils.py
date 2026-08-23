from typing import Any, Callable, TypeVar
import nt_flowwow_seller_client._respmodels as respmodels


def make_shop_page(raw_page: dict[str, Any]) -> respmodels.FwPage[respmodels.FwShop]:
    return respmodels.FwPage(raw_page, "shops", respmodels.FwShop)


def make_product_page(raw_page: dict[str, Any]) -> respmodels.FwPage[respmodels.FwProduct]:
    return respmodels.FwPage(raw_page, "items", respmodels.FwProduct)


def make_order_page(raw_page: dict[str, Any]) -> respmodels.FwPage[respmodels.FwOrder]:
    return respmodels.FwPage(raw_page, "items", respmodels.FwOrder)


T = TypeVar("T")

def verify_pages_equal(e: respmodels.FwPage[T], a: respmodels.FwPage[T], vf: Callable[[T, T], None]) -> None:
    assert e.raw == a.raw
    assert e.total == a.total
    assert len(e.items) == len(a.items)
    for a_item, b_item in zip(e.items, a.items):
        vf(a_item, b_item)


def verify_shops_equal(e: respmodels.FwShop, a: respmodels.FwShop) -> None:
    assert e.raw == a.raw
    assert e.shop_id == a.shop_id
    assert e.name == a.name
    assert e.status == a.status
    assert e.is_verified == a.is_verified


def verify_products_equal(e: respmodels.FwProduct, a: respmodels.FwProduct) -> None:
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


def verify_order_items_equal(e: respmodels.FwOrderItem, a: respmodels.FwOrderItem) -> None:
    assert e.raw == a.raw
    assert e.offer_id == a.offer_id
    assert e.product_id == a.product_id
    assert e.count == a.count
    assert e.cost == a.cost


def verify_orders_equal(e: respmodels.FwOrder, a: respmodels.FwOrder) -> None:
    assert e.raw == a.raw
    assert e.id == a.id
    assert e.created_date == a.created_date
    assert e.status == a.status
    assert e.delivery_type == a.delivery_type
    assert e.courier_info == a.courier_info
    assert e.shop_additional_info == a.shop_additional_info
    assert e.comment == a.comment
    assert e.message == a.message
    assert e.user_name == a.user_name
    assert e.recipient_name == a.recipient_name
    if e.products is None:
        assert a.products is None
    else:
        assert len(e.products) == len(a.products)
        for ep, ap in zip(e.products, a.products):
            verify_order_items_equal(ep, ap)


def _verify_flat_product_errors_equal(e: respmodels.FwFlatProductRespErr, a: respmodels.FwFlatProductRespErr) -> None:
    assert e.raw == a.raw
    assert e.offer_id == a.offer_id
    assert e.product_id == a.product_id
    assert e.message == a.message


def verify_offer_mapping_errors_equal(
    e_list: list[respmodels.FwOfferMappingRespErr], a_list: list[respmodels.FwOfferMappingRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)


def verify_product_activeness_errors_equal(
    e_list: list[respmodels.FwProductActiveRespErr], a_list: list[respmodels.FwProductActiveRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)
        assert e.is_active == a.is_active


def verify_stock_updating_errors_equal(
    e_list: list[respmodels.FwStockUpdatingRespErr], a_list: list[respmodels.FwStockUpdatingRespErr],
) -> None:
    assert len(e_list) == len(a_list)
    for e, a in zip(e_list, a_list):
        _verify_flat_product_errors_equal(e, a)
        assert e.stock == a.stock
