from typing import Any
from enum import StrEnum
from ._validation import validate, is_int32_id_valid, is_offer_id_valid, is_stock_valid


class FwShopStatus(StrEnum):
    ACTIVE = "active"
    MODERATION = "moderation"
    DISABLED = "disabled"


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
