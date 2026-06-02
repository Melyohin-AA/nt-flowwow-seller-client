import aiohttp
from typing import Any, Iterable, TypeVar
from .errors import _make_bad_resp_err_der_from_code
from .reqmodels import FwShopStatus, FwOfferMapping, FwProductStock
from .respmodels import FwPage, FwShop, FwProduct, FwOfferMappingError, FwProductActiveError, FwStockUpdatingError
from ._validation import (
    validate, validate_query_list,
    is_token_valid, is_int32_id_valid, is_offer_id_valid,
    is_page_valid, is_shop_limit_valid, is_product_limit_valid, is_product_type_valid,
)


def _authorize(token: str, headers: dict[str, str]) -> dict[str, str]:
    headers["Authorization"] = f"Bearer {token}"
    return headers


def _check_response_status(code: int) -> None:
    if code != 200:
        raise _make_bad_resp_err_der_from_code(code)


TRespErr = TypeVar("TRespErr")

def _parse_ok_response_error_list(content: Any, t: type[TRespErr]) -> list[TRespErr]:#//~ test
    if isinstance(content, dict) and (errors := content.get("errors")) and errors:
        return [
            t(err)  # type: ignore[call-arg]
            for err in errors if isinstance(err, dict)
        ]
    return []


class FwClient:
    def __init__(self, domain="apis.flowwow.com") -> None:
        self._domain = domain
        self._http = aiohttp.ClientSession()

    async def close(self) -> None:
        """Releases resources. An object and its child objects must not be used after calling this method"""
        await self._http.close()

    def merchant(self, token: str) -> "FwClient.Merchant":
        """
        Makes a child object for a merchant.

        :param token: Merchant's bearer token; non-empty string limited to 4095 chars
        :type token: str
        :return: A new merchant child object
        :rtype: FwClient.Merchant
        :raises FwValidationError:
        :raises FwError:
        """
        return FwClient.Merchant(self, token)

    class Merchant:
        def __init__(self, client: "FwClient", token: str) -> None:
            """internal"""
            self._c = client
            self._token = validate("token", token, is_token_valid)

        def shop(self, shop_id: int) -> "FwClient.Shop":
            """
            Makes a child object for a shop.

            :param shop_id: Shop ID; integer in [1, 2^32-1] range
            :type shop_id: int
            :return: A new shop child object
            :rtype: FwClient.Shop
            :raises FwValidationError:
            :raises FwError:
            """
            return FwClient.Shop(self, shop_id)

        async def get_shops(
            self, status: FwShopStatus, page=0, limit=50, *,
            shop_ids: list[int] | None = None,
        ) -> FwPage[FwShop]:
            """
            Retrieves paged shops of the merchant from endpoint
            [`/apiseller/shops`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-shops).

            :param status: Status of shops to be requested
            :type status: FwShopStatus
            :param page: Number of page to be requested; non-negative integer
            :type page: int
            :param limit: Max page size; integer in [1, 50] range
            :type limit: int
            :param shop_ids: IDs of shops to be requested; list of integers in [1, 2^32-1] range
            :type shop_ids: list[int] | None
            :return: A page of requested shops
            :rtype: FwPage[FwShop]
            :raises FwValidationError:
            :raises FwBadResponseStatusError:
            :raises FwParsingError:
            :raises FwError:
            """
            url = f"https://{self._c._domain}/apiseller/shops"
            body = {
                "status": status.value,
                "page": validate("page", page, is_page_valid),
                "limit": validate("limit", limit, is_shop_limit_valid),
            }
            if shop_ids:
                body["shopIds"] = validate_query_list("shop_ids", shop_ids, is_int32_id_valid)
            headers = _authorize(self._token, {})
            async with self._c._http.post(url, headers=headers, json=body) as resp:
                _check_response_status(resp.status)
                content = await resp.json()
            return FwPage(content, "shops", FwShop)

    class Shop:
        def __init__(self, merchant: "FwClient.Merchant", shop_id: int) -> None:
            """internal"""
            self._m = merchant
            self._shop_id = validate("shop_id", shop_id, is_int32_id_valid)

        # Products

        async def get_products(
            self, page=0, limit=1000, *,
            offer_ids: list[str] | None = None,
            product_ids: list[int] | None = None,
            category_ids: list[int] | None = None,
            type: int | None = None,
        ) -> FwPage[FwProduct]:
            """
            Retrieves paged products of the shop from endpoint
            [`/apiseller/products`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products).

            :param page: Number of page to be requested; non-negative integer
            :type page: int
            :param limit: Max page size; integer in [1, 1000] range
            :type limit: int
            :param offer_ids: Offer IDs of products to be requested; list of non-empty strings limited to 50 chars
            :type offer_ids: list[str] | None
            :param product_ids: Product IDs of products to be requested; list of integers in [1, 2^32-1] range
            :type product_ids: list[int] | None
            :param category_ids: Category IDs of products to be requested; list of integers in [1, 2^32-1] range
            :type category_ids: list[int] | None
            :return: A page of requested products
            :rtype: FwPage[FwProduct]
            :raises FwValidationError:
            :raises FwBadResponseStatusError:
            :raises FwParsingError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/products?shopId={self._shop_id}"
            body = {
                "page": validate("page", page, is_page_valid),
                "limit": validate("limit", limit, is_product_limit_valid),
            }
            if offer_ids:
                body["offerIds"] = validate_query_list("offer_ids", offer_ids, is_offer_id_valid)
            if product_ids:
                body["productIds"] = validate_query_list("product_ids", product_ids, is_int32_id_valid)
            if category_ids:
                body["categoryIds"] = validate_query_list("category_ids", category_ids, is_int32_id_valid)
            if type:
                body["type"] = validate("type", type, is_product_type_valid)
            headers = _authorize(self._m._token, {})
            async with self._m._c._http.post(url, headers=headers, json=body) as resp:
                _check_response_status(resp.status)
                content = await resp.json()
            return FwPage(content, "items", FwProduct)

        async def map_offers(self, mappings: Iterable[FwOfferMapping]) -> list[FwOfferMappingError]:
            """
            Maps specified external offer IDs with corresponding products via endpoint
            [`/apiseller/products/offersMappings`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products-offersmappings).

            Requested changes may be applied partially. In that case, a list of errors will be returned.

            :param offer_ids: Offer ID to product ID mappings
            :type offer_ids: Iterable[FwOfferMapping]
            :return: A list of partial errors
            :rtype: list[FwOfferMappingError]
            :raises FwBadResponseStatusError:
            :raises FwParsingError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/products/offersMappings?shopId={self._shop_id}"
            body = {"offers": [m.to_json() for m in mappings]}
            headers = _authorize(self._m._token, {})
            async with self._m._c._http.post(url, headers=headers, json=body) as resp:
                _check_response_status(resp.status)
                content = await resp.json()
            return _parse_ok_response_error_list(content, FwOfferMappingError)

        async def set_product_active(self, offer_ids: Iterable[str], active: bool) -> list[FwProductActiveError]:
            """
            Hides or unhides specified products via either endpoint
            [`/apiseller/products/hide`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products-hide)
            or
            [`/apiseller/products/unhide`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products-unhide).

            Requested changes may be applied partially. In that case, a list of errors will be returned.

            :param offer_ids: Offer IDs of products to be hid/unhid; non-empty strings limited to 50 chars
            :type offer_ids: Iterable[str]
            :param active: `False` to hide, `True` to unhide
            :type active: bool
            :return: A list of partial errors
            :rtype: list[FwProductActiveError]
            :raises FwValidationError:
            :raises FwBadResponseStatusError:
            :raises FwParsingError:
            :raises FwError:
            """
            action = "unhide" if active else "hide"
            url = f"https://{self._m._c._domain}/apiseller/products/{action}?shopId={self._shop_id}"
            body = {"offers": [{"offerId": validate("offer_ids[i]", oid, is_offer_id_valid)} for oid in offer_ids]}
            headers = _authorize(self._m._token, {})
            async with self._m._c._http.post(url, headers=headers, json=body) as resp:
                _check_response_status(resp.status)
                content = await resp.json()
            return _parse_ok_response_error_list(content, FwProductActiveError)

        # Stocks

        async def update_stocks(self, changes: Iterable[FwProductStock]) -> list[FwStockUpdatingError]:
            """
            Updates stock quantities of specified products via endpoint
            [`/apiseller/stocks/put`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#put-apiseller-stocks-put).

            Requested changes may be applied partially. In that case, a list of errors will be returned.

            :param changes: Changes in product stocks to be pushed
            :type changes: Iterable[FwProductStock]
            :return: A list of partial errors
            :rtype: list[FwStockUpdatingError]
            :raises FwBadResponseStatusError:
            :raises FwParsingError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/stocks/put?shopId={self._shop_id}"
            body = {"offers": [c.to_json() for c in changes]}
            headers = _authorize(self._m._token, {})
            async with self._m._c._http.put(url, headers=headers, json=body) as resp:
                _check_response_status(resp.status)
                content = await resp.json()
            return _parse_ok_response_error_list(content, FwStockUpdatingError)
