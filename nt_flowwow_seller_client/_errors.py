from typing import Any


class FwError(Exception):
    """Base error type of the package"""

    def __init__(self, *args) -> None:
        super().__init__(*args)


class FwInitializationError(FwError):
    """Represents a client initialization error"""


class FwFinalizationError(FwError):
    """Represents a client finalization error"""


class FwValidationError(FwError):
    """Represents a user data validation error"""

    def __init__(self, attr: str, value: Any) -> None:
        super().__init__(f"{attr} has invalid value: {value}")


class FwParsingError(FwError):
    """Represents a response parsing error"""

    def __init__(self, attr: str, issue: str) -> None:
        super().__init__(f"Failed to parse {attr}: {issue}")


class FwNetworkError(FwError):
    """Represents a client network error"""


class FwBadResponseStatusError(FwError):
    """Represents a non-2xx response error"""

    def __init__(self, code: int, msg: str) -> None:
        self.__code = code
        super().__init__(msg)

    @property
    def code(self) -> int:
        """Response status code"""
        return self.__code


class FwUnexpectedResponseStatusError(FwBadResponseStatusError):
    """Represents an unexpected response error"""

    def __init__(self, code: int) -> None:
        super().__init__(code, f"Unexpected response status: {code}")


class FwTokenRejectedError(FwBadResponseStatusError):
    """Represents an authorization error. Corresponds to response 401"""

    def __init__(self) -> None:
        super().__init__(401, "Token has been rejected")


class FwNotFoundError(FwBadResponseStatusError):
    """Represents a resource not found error. Corresponds to response 404"""

    def __init__(self) -> None:
        super().__init__(404, "Resource not found")


class FwTooManyRequestsError(FwBadResponseStatusError):
    """Represents a too many requests error. Corresponds to response 429"""

    def __init__(self) -> None:
        super().__init__(429, "Too many requests")


_BAD_RESP_ERR_DERS = {
    401: FwTokenRejectedError,
    404: FwNotFoundError,
    429: FwTooManyRequestsError,
}


def make_bad_resp_err_der_from_code(code: int) -> FwBadResponseStatusError:
    return der() if (der := _BAD_RESP_ERR_DERS.get(code)) else FwUnexpectedResponseStatusError(code)
