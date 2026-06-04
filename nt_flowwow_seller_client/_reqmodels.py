from typing import Any
from enum import StrEnum
from ._validation import validate, validate_query_list, is_int32_id_valid, is_offer_id_valid, is_stock_valid


class FwShopStatus(StrEnum):
    ACTIVE = "active"
    MODERATION = "moderation"
    DISABLED = "disabled"


class FwProductIdQueryList:
    def __init__(self, product_ids: list[int]) -> None:
        """
        :param product_ids: Product IDs of products to be requested; list of integers in [1, 2^32-1] range
        :type product_ids: list[int]
        :raises FwValidationError:
        :raises FwError:
        """
        self._product_ids = validate_query_list("product_ids", product_ids, is_int32_id_valid)


class FwOfferIdQueryList:
    def __init__(self, offer_ids: list[str]) -> None:
        """
        :param offer_ids: Offer IDs of products to be requested; list of non-empty strings limited to 50 chars
        :type offer_ids: list[str]
        :raises FwValidationError:
        :raises FwError:
        """
        self._offer_ids = validate_query_list("offer_ids", offer_ids, is_offer_id_valid)


class FwOfferMapping:
    def __init__(self, product_id: int, offer_id: str) -> None:
        """
        :param product_id: Product ID of a product; integer in [1, 2^32-1] range
        :type product_id: int
        :param offer_id: Offer ID of a product; non-empty string limited to 50 chars
        :type offer_id: str
        :raises FwValidationError:
        :raises FwError:
        """
        self._product_id = validate("product_id", product_id, is_int32_id_valid)
        self._offer_id = validate("offer_id", offer_id, is_offer_id_valid)

    def to_json(self) -> dict[str, Any]:
        return {
            "offerId": self._offer_id,
            "productId": self._product_id,
        }


class FwProductStock:
    def __init__(self, offer_id: str, stock: int) -> None:
        """
        :param offer_id: Offer ID of a product; non-empty string limited to 50 chars
        :type offer_id: str
        :param stock: Stock quantity of a product; integer in [0, 2^32-1] range
        :type stock: int
        :raises FwValidationError:
        :raises FwError:
        """
        self._offer_id = validate("offer_id", offer_id, is_offer_id_valid)
        self._stock = validate("stock", stock, is_stock_valid)

    def to_json(self) -> dict[str, Any]:
        return {
            "offerId": self._offer_id,
            "stock": self._stock,
        }
