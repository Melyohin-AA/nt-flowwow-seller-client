import aiohttp
import datetime
from typing import Any, Iterable, TypeVar
from ._errors import (
    make_bad_resp_err_der_from_code,
    FwError, FwInitializationError, FwFinalizationError, FwParsingError, FwNetworkError,
)
from ._reqmodels import FwShopStatus, FwProductIdQueryList, FwOfferIdQueryList, FwOfferMapping, FwProductStock
from ._respmodels import (
    _validate_type,
    FwPage, FwShop, FwProduct, FwOrder, FwOfferMappingRespErr, FwProductActiveRespErr, FwStockUpdatingRespErr,
)
from ._validation import (
    validate, validate_query_list, validate_token, is_int32_valid, is_int32_id_valid, is_offer_id_valid,
    is_page_valid, is_shop_limit_valid, is_product_limit_valid, is_order_limit_valid, is_product_type_valid,
)


def _authorize(token: str, headers: dict[str, str]) -> dict[str, str]:
    headers["Authorization"] = f"Bearer {token}"
    return headers


def _check_response_status(code: int) -> None:
    if code // 100 != 2:
        raise make_bad_resp_err_der_from_code(code)


TRespErr = TypeVar("TRespErr")

def _parse_ok_resp_error_list(content: Any, t: type[TRespErr]) -> list[TRespErr]:
    if (errors := _validate_type("resp.content", content, dict).get("errors")) and errors:
        return [
            t(err)  # type: ignore[call-arg]
            for err in _validate_type("errors", errors, list)
        ]
    return []


class FwClient:
    def __init__(self) -> None:
        """
        Intializes an instance and allocates resources for it.

        Note: Requires a running event loop.

        :raises FwInitializationError:
        :raises FwError:
        """
        self._domain = "apis.flowwow.com"
        try:
            self._http = aiohttp.ClientSession()
        except Exception as err:
            raise FwInitializationError(err)

    async def close(self) -> None:
        """
        Finalizes an instance releasing its resources.

        Note: An object and its child objects must not be used after calling this method.

        :raises FwFinalizationError:
        :raises FwError:
        """
        try:
            await self._http.close()
        except Exception as err:
            raise FwFinalizationError(err)

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

    async def _request(self, *args, **kwargs) -> Any:
        try:
            async with self._http.request(*args, **kwargs) as resp:
                _check_response_status(resp.status)
                return await resp.json()
        except FwError:
            raise
        except ValueError as err:
            raise FwParsingError("resp.content", str(err))
        except aiohttp.ContentTypeError as err:
            raise FwParsingError("resp.content-type", str(err))
        except Exception as err:
            raise FwNetworkError(err)

    class Merchant:
        def __init__(self, client: "FwClient", token: str) -> None:
            """internal"""
            self._c = client
            self._token = validate_token(token)

        @property
        def client(self) -> "FwClient":
            return self._c

        def shop(self, shop_id: int) -> "FwClient.Shop":
            """
            Makes a child object for a shop.

            :param shop_id: Shop ID; integer in [1, 2^32) range
            :type shop_id: int
            :return: A new shop child object
            :rtype: FwClient.Shop
            :raises FwValidationError:
            :raises FwError:
            """
            return FwClient.Shop(self, shop_id)

        async def get_shops(
            self, status=FwShopStatus.ACTIVE, page=0, limit=50, *,
            shop_ids: list[int] | None = None,
        ) -> FwPage[FwShop]:
            """
            Retrieves paged shops of the merchant from endpoint
            [`/apiseller/shops`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-shops).

            Note: The endpoint does not take empty id lists into account,
            so passing empty `shop_ids` will be equal to not specifying it at all.

            :param status: Status of shops to be requested
            :type status: FwShopStatus
            :param page: Number of page to be requested; non-negative integer
            :type page: int
            :param limit: Max page size; integer in [1, 50] range
            :type limit: int
            :param shop_ids: IDs of shops to be requested; list of integers in [1, 2^32) range
            :type shop_ids: list[int] | None
            :return: A page of requested shops
            :rtype: FwPage[FwShop]
            :raises FwValidationError:
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            url = f"https://{self._c._domain}/apiseller/shops"
            body = {
                "status": status.value,
                "page": validate("page", page, is_page_valid),
                "limit": validate("limit", limit, is_shop_limit_valid),
            }
            if shop_ids is not None:
                body["shopIds"] = validate_query_list("shop_ids", shop_ids, is_int32_id_valid)
            headers = _authorize(self._token, {})
            content = await self._c._request("post", url, headers=headers, json=body)
            return FwPage(content, "shops", FwShop)

    class Shop:
        def __init__(self, merchant: "FwClient.Merchant", shop_id: int) -> None:
            """internal"""
            self._m = merchant
            self._shop_id = validate("shop_id", shop_id, is_int32_id_valid)

        @property
        def merchant(self) -> "FwClient.Merchant":
            return self._m

        @property
        def shop_id(self) -> int:
            return self._shop_id

        # Products

        async def get_products(
            self, page=0, limit=1000, *,
            ids: FwProductIdQueryList | FwOfferIdQueryList | None = None,
            category_ids: list[int] | None = None,
            product_type: int | None = None,
        ) -> FwPage[FwProduct]:
            """
            Retrieves paged products of the shop from endpoint
            [`/apiseller/products`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products).

            Note: The endpoint does not take empty id lists into account,
            so passing empty `ids` or `category_ids` will be equal to not specifying them at all.

            :param page: Number of page to be requested; non-negative integer
            :type page: int
            :param limit: Max page size; integer in [1, 1000] range
            :type limit: int
            :param ids: Product/Offer IDs of products to be requested
            :type ids: FwProductIdQueryList | FwOfferIdQueryList | None
            :param category_ids: Category IDs of products to be requested; list of integers in [1, 2^32) range
            :type category_ids: list[int] | None
            :param product_type: Product Type ID of products to be requested; integer in {1, 2, 3} set
            :type product_type: int | None
            :return: A page of requested products
            :rtype: FwPage[FwProduct]
            :raises FwValidationError:
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/products?shopId={self._shop_id}"
            body: dict[str, Any] = {
                "page": validate("page", page, is_page_valid),
                "limit": validate("limit", limit, is_product_limit_valid),
            }
            if type(ids) is FwProductIdQueryList:
                body["productIds"] = ids._product_ids
            elif type(ids) is FwOfferIdQueryList:
                body["offerIds"] = ids._offer_ids
            if category_ids is not None:
                body["categoryIds"] = validate_query_list("category_ids", category_ids, is_int32_id_valid)
            if product_type is not None:
                body["type"] = validate("type", product_type, is_product_type_valid)
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("post", url, headers=headers, json=body)
            return FwPage(content, "items", FwProduct)

        async def map_offers(self, mappings: Iterable[FwOfferMapping]) -> list[FwOfferMappingRespErr]:
            """
            Maps specified external offer IDs with corresponding products via endpoint
            [`/apiseller/products/offersMappings`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#post-apiseller-products-offersmappings).

            Requested changes may be applied partially. In that case, a list of errors will be returned.

            :param offer_ids: Offer ID to product ID mappings
            :type offer_ids: Iterable[FwOfferMapping]
            :return: A list of partial errors
            :rtype: list[FwOfferMappingRespErr]
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/products/offersMappings?shopId={self._shop_id}"
            body = {"offers": [m.to_json() for m in mappings]}
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("post", url, headers=headers, json=body)
            return _parse_ok_resp_error_list(content, FwOfferMappingRespErr)

        async def set_product_active(self, offer_ids: Iterable[str], active: bool) -> list[FwProductActiveRespErr]:
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
            :rtype: list[FwProductActiveRespErr]
            :raises FwValidationError:
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            action = "unhide" if active else "hide"
            url = f"https://{self._m._c._domain}/apiseller/products/{action}?shopId={self._shop_id}"
            body = {"offers": [{"offerId": validate("offer_ids[i]", o, is_offer_id_valid)} for o in offer_ids]}
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("post", url, headers=headers, json=body)
            return _parse_ok_resp_error_list(content, FwProductActiveRespErr)

        # Stocks

        async def update_stocks(self, changes: Iterable[FwProductStock]) -> list[FwStockUpdatingRespErr]:
            """
            Updates stock quantities of specified products via endpoint
            [`/apiseller/stocks/put`](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#put-apiseller-stocks-put).

            Requested changes may be applied partially. In that case, a list of errors will be returned.

            :param changes: Changes in product stocks to be pushed
            :type changes: Iterable[FwProductStock]
            :return: A list of partial errors
            :rtype: list[FwStockUpdatingRespErr]
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            url = f"https://{self._m._c._domain}/apiseller/stocks/put?shopId={self._shop_id}"
            body = {"offers": [c.to_json() for c in changes]}
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("put", url, headers=headers, json=body)
            return _parse_ok_resp_error_list(content, FwStockUpdatingRespErr)

        # Orders

        async def get_order(self, order_id: int) -> FwOrder:
            """
            Retrieves an order via endpoint
            [`/apiseller/orders/view`](https://seller-docs.flowwow.com/5.-instrumenty-prodavca/5.1-dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#get-apiseller-orders-view).

            :param order_id: ID of the requested order; integer in [1, 2^32) range
            :type order_id: int
            :return: Order
            :rtype: FwOrder
            :raises FwValidationError:
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            validate("orderId", order_id, is_int32_id_valid)
            url = f"https://{self._m._c._domain}/apiseller/orders/view?shopId={self._shop_id}&orderId={order_id}"
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("get", url, headers=headers)
            return FwOrder(content)

        async def get_orders(
            self, page=0, limit=100, *,
            order_id: int | None = None,
            created_date: datetime.date | None = None,
            delivery_date_from: datetime.date | None = None,
            delivery_date_to: datetime.date | None = None,
            status: int | None = None,
            delivery_type: int | None = None,
            delivery_time_type: int | None = None,
        ) -> FwPage[FwOrder]:
            """
            Retrieves paged orders of the shop from endpoint
            [`/apiseller/orders/list`](https://seller-docs.flowwow.com/5.-instrumenty-prodavca/5.1-dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1#get-apiseller-orders-list).

            Parameters `status`, `delivery_type`, `delivery_time_type` are not fully validated.
            A value may pass the validation but still be rejected by the API.
            It is recommended to take values directly from the API's responses.

            :param page: Number of page to be requested, corrected; non-negative integer
            :type page: int
            :param limit: Max page size; integer in [1, 100] range
            :type limit: int
            :param order_id: Order ID; integer in [1, 2^32) range
            :type order_id: int | None
            :param created_date: Order's creation date
            :type created_date: datetime.date | None
            :param delivery_date_from: Order's delivery date from
            :type delivery_date_from: datetime.date | None
            :param delivery_date_to: Order's delivery date to
            :type delivery_date_to: datetime.date | None
            :param status: Order Status ID; integer in [0, 2^32) range
            :type status: int | None
            :param delivery_type: Order Delivery Type ID; integer in [0, 2^32) range
            :type delivery_type: int | None
            :param delivery_time_type: Order Delivery Time Type ID; integer in [0, 2^32) range
            :type delivery_time_type: int | None
            :return: A page of requested orders
            :rtype: FwPage[FwOrder]
            :raises FwValidationError:
            :raises FwParsingError:
            :raises FwNetworkError:
            :raises FwBadResponseStatusError:
            :raises FwError:
            """
            DATE_FORMAT = "%Y-%m-%d"
            qb = [
                f"shopId={self._shop_id}",
                f"page={validate('page', page, is_page_valid) + 1}",
                f"limit={validate('limit', limit, is_order_limit_valid)}",
            ]
            if order_id is not None:
                qb.append(f"id={validate('orderId', order_id, is_int32_id_valid)}")
            if created_date is not None:
                qb.append(f"createdDate={created_date.strftime(DATE_FORMAT)}")
            if delivery_date_from is not None:
                qb.append(f"deliveryDateFrom={delivery_date_from.strftime(DATE_FORMAT)}")
            if delivery_date_to is not None:
                qb.append(f"deliveryDateTo={delivery_date_to.strftime(DATE_FORMAT)}")
            if status is not None:
                qb.append(f"status={validate('status', status, is_int32_valid)}")
            if delivery_type is not None:
                qb.append(f"deliveryType={validate('deliveryType', delivery_type, is_int32_valid)}")
            if delivery_time_type is not None:
                qb.append(f"deliveryTimeType={validate('deliveryTimeType', delivery_time_type, is_int32_valid)}")
            url = f"https://{self._m._c._domain}/apiseller/orders/list?{'&'.join(qb)}"
            headers = _authorize(self._m._token, {})
            content = await self._m._c._request("get", url, headers=headers)
            return FwPage(content, "items", FwOrder)
