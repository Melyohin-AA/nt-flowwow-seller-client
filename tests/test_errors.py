import pytest
import nt_flowwow_seller_client._errors as e


@pytest.mark.parametrize(
    "code, expected_error_type",
    [
        (401, e.FwTokenRejectedError),
        (404, e.FwNotFoundError),
        (429, e.FwTooManyRequestsError),
        (500, e.FwUnexpectedResponseStatusError),
        (400, e.FwUnexpectedResponseStatusError),
        (202, e.FwUnexpectedResponseStatusError),
        (123, e.FwUnexpectedResponseStatusError),
    ]
)
def test_make_bad_resp_err_der_from_code(code, expected_error_type):
    err = e.make_bad_resp_err_der_from_code(code)
    assert err.code == code
    assert type(err) is expected_error_type
