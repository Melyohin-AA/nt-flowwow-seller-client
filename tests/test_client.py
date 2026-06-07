from typing import Any, AsyncGenerator
import pytest
import pytest_asyncio
from aioresponses import aioresponses
import nt_flowwow_seller_client._errors as errors
import nt_flowwow_seller_client._reqmodels as reqmodels
import nt_flowwow_seller_client._respmodels as respmodels
from nt_flowwow_seller_client._client import FwClient, _authorize, _parse_ok_response_error_list
import tests.model_utils as model_utils


SHOP_ID = 987654
TOKEN = "tok456"


def verify_request(actual_reqs: list, expected_url: str, expected_body: Any) -> None:
    assert len(actual_reqs) == 1
    actual_url, actual_kwargs = actual_reqs[0]
    assert str(actual_url) == expected_url
    assert actual_kwargs["json"] == expected_body


def verify_request_(
    actual_reqs: dict, expected_method: str, expected_url: str, expected_headers: Any, expected_body: Any,
) -> None:
    assert len(actual_reqs) == 1
    actual_req = next(iter(actual_reqs.items()))
    assert actual_req[0][0] == expected_method
    assert str(actual_req[0][1]) == expected_url
    actual_kwargs = actual_req[1][0].kwargs
    assert actual_kwargs["headers"] == expected_headers
    assert actual_kwargs["json"] == expected_body


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[FwClient, Any]:
    client = FwClient()
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_make_close_client():
    # make
    client = FwClient()
    assert client._domain == "apis.flowwow.com"
    assert not client._http.closed
    # close
    await client.close()
    assert client._http.closed
    # close twice
    await client.close()
    assert client._http.closed


@pytest.mark.asyncio
async def test_make_child_objects(client: FwClient):
    # arrange
    TOKEN = "tok123"
    SHOP_ID = 123456
    # act
    merchant = client.merchant(TOKEN)
    shop = merchant.shop(SHOP_ID)
    # assert
    assert merchant._c == client
    assert merchant._token == TOKEN
    assert shop._m == merchant
    assert shop._shop_id == SHOP_ID


@pytest.mark.parametrize(
    "token, headers, expected",
    [
        ("tok123", {}, {"Authorization": "Bearer tok123"}),
        ("tok456", {"x": "y"}, {"x": "y", "Authorization": "Bearer tok456"}),
    ]
)
def test_authorize(token, headers, expected):
    assert _authorize(token, headers) == expected


@pytest.mark.parametrize(
    "content, expected_errors",
    [
        (
            {
                "shopId": 1, "summary": {}, "data": [],
                "errors": [
                    {"offerId": "1001", "productId": 101001, "message": "nope"},
                    {"offerId": "1002", "productId": 101002, "message": "nah"},
                ]
            },
            [
                respmodels.FwOfferMappingRespErr({"offerId": "1001", "productId": 101001, "message": "nope"}),
                respmodels.FwOfferMappingRespErr({"offerId": "1002", "productId": 101002, "message": "nah"}),
            ]
        ),
        ({"shopId": 1, "summary": {}, "data": [], "errors": []}, []),
        ({"shopId": 1, "summary": {}, "data": []}, []),
        ("try get errors from this", []),
    ]
)
def test_parse_ok_response_error_list(content, expected_errors):
    actual_errors = _parse_ok_response_error_list(content, respmodels.FwOfferMappingRespErr)
    model_utils.verify_offer_mapping_errors_equal(expected_errors, actual_errors)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url, url_ow, headers, body, code, resp_data, expected_content, expected_errt",
    [
        ("http://host.name/path?k=v", None, {}, {"a": 1}, 200, '{"b": 2}', {"b": 2}, None),
        ("https://a.b.c/", None, {"h": "v"}, ["a", "b"], 201, "{", None, errors.FwParsingError),
        ("https://a.b/", "https://c.d/", {}, [], 202, "{}", None, errors.FwNetworkError),
        ("http://a.b/c", None, {}, {}, 500, "{}", None, errors.FwUnexpectedResponseStatusError),
        ("http://a.b/c", None, {}, {}, 401, "{}", None, errors.FwTokenRejectedError),
        ("http://a.b/c", None, {}, {}, 404, "{}", None, errors.FwNotFoundError),
        ("http://a.b/c", None, {}, {}, 429, "{}", None, errors.FwTooManyRequestsError),
    ]
)
async def test_request(client: FwClient, url, url_ow, headers, body, code, resp_data, expected_content, expected_errt):
    try:
        with aioresponses() as mocked:
            # mock
            mocked.patch(url, body=resp_data, status=code)
            # act
            actual_content = await client._request("PATCH", url_ow or url, headers=headers, json=body)
            # assert
            assert expected_errt is None
            assert actual_content == expected_content
            mocked.assert_called_once_with(url_ow or url, method="PATCH", headers=headers, json=body)
    except errors.FwError as err:
        assert expected_content is None
        assert isinstance(err, expected_errt)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, page, limit, shop_ids, expected_shops, expected_body",
    [
        (
            reqmodels.FwShopStatus.ACTIVE, 0, 48, None,
            model_utils.make_shop_page({"shops": [], "total": 0}),
            {"status": reqmodels.FwShopStatus.ACTIVE.value, "page": 0, "limit": 48}
        ),
        (
            reqmodels.FwShopStatus.DISABLED, 2, 34, None,
            model_utils.make_shop_page({
                "shops": [{
                    "shopId": 101,
                    "name": "shop1",
                    "status": "disabled",
                    "address": "a, b, c",
                    "currency": "KZT",
                    "isVerified": True,
                    "workingDays": ["1", "2", "3", "4", "5"]
                }],
                "total": 69
            }), {"status": reqmodels.FwShopStatus.DISABLED.value, "page": 2, "limit": 34}
        ),
        (
            reqmodels.FwShopStatus.MODERATION, 1, 2, [1, 2, 3],
            model_utils.make_shop_page({"shops": [], "total": 0}),
            {"status": reqmodels.FwShopStatus.MODERATION.value, "page": 1, "limit": 2, "shopIds": [1, 2, 3]}
        ),
    ]
)
async def test_get_shops(
    client: FwClient,
    status, page, limit, shop_ids,
    expected_shops, expected_body,
):
    URL = "https://apis.flowwow.com/apiseller/shops"
    with aioresponses() as mocked:
        # mock
        mocked.post(URL, payload=expected_shops.raw)
        # act
        merchant = client.merchant(TOKEN)
        actual_shops = await merchant.get_shops(status, page, limit, shop_ids=shop_ids)
        # assert
        mocked.assert_called_once()
        verify_request_(mocked.requests, "post", URL, _authorize(TOKEN, {}), expected_body)
        model_utils.verify_pages_equal(expected_shops, actual_shops, model_utils.verify_shops_equal)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, limit, ids, category_ids, type, expected_products, expected_body",
    [
        (
            0, 498, reqmodels.FwProductIdQueryList([123, 456]), [7, 8], 2,
            model_utils.make_product_page({"items": [], "total": 0}), {
                "page": 0, "limit": 498,
                "productIds": [123, 456],
                "categoryIds": [7, 8],
                "type": 2,
            }
        ),
        (
            0, 420, reqmodels.FwOfferIdQueryList(["FLOW-001", "FLOW-002"]), [3], 1,
            model_utils.make_product_page({"items": [], "total": 0}), {
                "page": 0, "limit": 420,
                "offerIds": ["FLOW-001", "FLOW-002"],
                "categoryIds": [3],
                "type": 1,
            }
        ),
        (
            2, 100, None, None, None,
            model_utils.make_product_page({
                "items": [{
                    "offerId": "OLAK5uy_nzaNSOqnI6dSpxpibb-5c7C6baXvlZUks",
                    "productId": 123,
                    "isActive": True,
                    "type": 1,
                    "categoryId": 1002001,
                    "subCategoryId": 100200101,
                    "name": "Flowerworks",
                    "description": "some description 1",
                    "url": "https://flowwow.com/product/flowerworks",
                    "available": 99999,
                    "stock": 100,
                    "minOrder": 1,
                    "price": "1.99",
                    "discount": "10",
                    "currencyCode": "EUR",
                    "images": ["https://cdn.example.com/images/a3644580212_10.jpg"],
                    "productionTime": 60,
                    "shipmentTime": 120,
                    "canRent": 0,
                    "originalId": 0,
                    "isDeliveryPost": False,
                    "isStarred": True,
                    "vat": "18"
                }],
                "total": 201
            }), {"page": 2, "limit": 100}
        ),
    ]
)
async def test_get_products(client: FwClient, page, limit, ids, category_ids, type, expected_products, expected_body):
    URL = f"https://apis.flowwow.com/apiseller/products?shopId={SHOP_ID}"
    with aioresponses() as mocked:
        # mock
        mocked.post(URL, payload=expected_products.raw)
        # act
        shop = client.merchant(TOKEN).shop(SHOP_ID)
        actual_products = await shop.get_products(page, limit, ids=ids, category_ids=category_ids, type=type)
        # assert
        mocked.assert_called_once()
        verify_request_(mocked.requests, "post", URL, _authorize(TOKEN, {}), expected_body)
        model_utils.verify_pages_equal(expected_products, actual_products, model_utils.verify_products_equal)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mappings, resp_body, expected_body",
    [
        (
            [reqmodels.FwOfferMapping(123456, "1098")],
            {
                "shopId": SHOP_ID,
                "summary": {
                    "total": 1, "success": 1, "failed": 0, "created": 0, "updated": 1, "relinked": 0, "unchanged": 0
                },
                "errors": []
            },
            {"offers": [{"offerId": "1098", "productId": 123456}]}
        ),
        (
            [reqmodels.FwOfferMapping(83418243, "1099")],
            {
                "shopId": SHOP_ID,
                "summary": {
                    "total": 1, "success": 0, "failed": 1, "created": 0, "updated": 0, "relinked": 0, "unchanged": 0
                },
                "errors": [
                    {
                        "offerId": "1099", "productId": 83418243,
                        "message": "Product not found"
                    }
                ]
            },
            {"offers": [{"offerId": "1099", "productId": 83418243}]}
        ),
    ]
)
async def test_map_offers(client: FwClient, mappings, resp_body, expected_body):
    URL = f"https://apis.flowwow.com/apiseller/products/offersMappings?shopId={SHOP_ID}"
    expected_errors = [respmodels.FwOfferMappingRespErr(err) for err in resp_body["errors"]]
    with aioresponses() as mocked:
        # mock
        mocked.post(URL, payload=resp_body)
        # act
        shop = client.merchant(TOKEN).shop(SHOP_ID)
        actual_errors = await shop.map_offers(mappings)
        # assert
        mocked.assert_called_once()
        verify_request_(mocked.requests, "post", URL, _authorize(TOKEN, {}), expected_body)
        model_utils.verify_offer_mapping_errors_equal(expected_errors, actual_errors)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offer_ids, active, action, resp_body, expected_body",
    [
        (
            [], False, "hide",
            {"shopId": SHOP_ID, "errors": []},
            {"offers": []}
        ),
        (
            [], True, "unhide",
            {"shopId": SHOP_ID, "errors": []},
            {"offers": []}
        ),
        (
            ["1098"], False, "hide",
            {"shopId": SHOP_ID, "errors": []},
            {"offers": [{"offerId": "1098"}]}
        ),
        (
            ["1099"], True, "unhide",
            {"shopId": SHOP_ID, "errors": []},
            {"offers": [{"offerId": "1099"}]}
        ),
        (
            ["1097"], False, "hide",
            {
                "shopId": SHOP_ID,
                "errors": [
                    {
                        "offerId": "1097", "productId": None, "isActive": True,
                        "message": "The passed offerId does not have an attached product"
                    }
                ]
            },
            {"offers": [{"offerId": "1097"}]}
        ),
        (
            ["1096"], True, "unhide",
            {
                "shopId": SHOP_ID,
                "errors": [
                    {
                        "offerId": "1096", "productId": None, "isActive": True,
                        "message": "The passed offerId does not have an attached product"
                    }
                ]
            },
            {"offers": [{"offerId": "1096"}]}
        ),
    ]
)
async def test_set_product_active(client: FwClient, offer_ids, active, action, resp_body, expected_body):
    URL = f"https://apis.flowwow.com/apiseller/products/{action}?shopId={SHOP_ID}"
    expected_errors = [respmodels.FwProductActiveRespErr(err) for err in resp_body["errors"]]
    with aioresponses() as mocked:
        # mock
        mocked.post(URL, payload=resp_body)
        # act
        shop = client.merchant(TOKEN).shop(SHOP_ID)
        actual_errors = await shop.set_product_active(offer_ids, active)
        # assert
        mocked.assert_called_once()
        verify_request_(mocked.requests, "post", URL, _authorize(TOKEN, {}), expected_body)
        model_utils.verify_product_activeness_errors_equal(expected_errors, actual_errors)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "changes, resp_body, expected_body",
    [
        (
            [],
            {"shopId": SHOP_ID, "errors": []},
            {"offers": []}
        ),
        (
            [reqmodels.FwProductStock("1098", 42)],
            {"shopId": SHOP_ID, "errors": []},
            {"offers": [{"offerId": "1098", "stock": 42}]}
        ),
        (
            [reqmodels.FwProductStock("1097", 41), reqmodels.FwProductStock("1099", 43)],
            {
                "shopId": SHOP_ID,
                "errors": [
                    {
                        "offerId": "1097",
                        "productId": 83418243,
                        "stock": 41,
                        "message": "idk"
                    },
                    {
                        "offerId": "1099",
                        "productId": None,
                        "stock": 43,
                        "message": "offerId is not associated with any item"
                    }
                ]
            },
            {
                "offers": [
                    {"offerId": "1097", "stock": 41},
                    {"offerId": "1099", "stock": 43},
                ]
            }
        ),
    ]
)
async def test_update_stocks(client: FwClient, changes, resp_body, expected_body):
    URL = f"https://apis.flowwow.com/apiseller/stocks/put?shopId={SHOP_ID}"
    expected_errors = [respmodels.FwStockUpdatingRespErr(err) for err in resp_body["errors"]]
    with aioresponses() as mocked:
        # mock
        mocked.put(URL, payload=resp_body)
        # act
        shop = client.merchant(TOKEN).shop(SHOP_ID)
        actual_errors = await shop.update_stocks(changes)
        # assert
        mocked.assert_called_once()
        verify_request_(mocked.requests, "put", URL, _authorize(TOKEN, {}), expected_body)
        model_utils.verify_stock_updating_errors_equal(expected_errors, actual_errors)
