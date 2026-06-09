# Python Client for Flowwow Seller API

This is an **inofficial** tiny and simple client for [Flowwow Seller API](https://seller-docs.flowwow.com/4.-instrumenty-prodavca/4.1.-integracii-i-api/dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1).

Limitations:
* Python version >= 3.10
* Async only

Currently supported endpoints:
* `/apiseller/shops`
* `/apiseller/products`
* `/apiseller/products/offersMappings`
* `/apiseller/products/hide` and `/apiseller/products/unhide`
* `/apiseller/stocks/put`

This project follows [SemVer](https://semver.org/) versioning scheme.

## Installation

```bash
pip install nt-flowwow-seller-client
```

## Reference

[Latest reference](https://melyohin-aa.github.io/nt-flowwow-seller-client/index.html)

## Usage

### Initialization and Finalization

`FwClient` is the entry point to all functionality of the package.

An `FwClient` instance allocates a new connection pool on initialization. That's why:
1. The instance should be finalized with the `close` method after using it to release the resources.
2. It is recommended to initialize the instance once, reuse it as much as possible, and finalize it at the end.

```python
from nt_flowwow_seller_client import FwClient

async def main() -> None:
    # Initializing a client instance
    client = FwClient()
    try:
        # Using the client
        await use_client(client)
    finally:
        # Finalizing the client
        await client.close()
        client = None
```

### Scopes

The package's functionality is divided into nested scopes. A scope can be obtained by creating a corresponding child object of a `FwClient` instance:
* `FwClient.Merchant`: **Merchant Scope** for requests which require an **Access Token**.
* `FwClient.Shop`: **Shop Scope** for which require a **Shop ID** and an **Access Token**.

```python
from nt_flowwow_seller_client import FwClient

def make_scopes(client: FwClient, token: str, shop_id: int) -> tuple[FwClient.Merchant, FwClient.Shop]:
    merchant: FwClient.Merchant = client.merchant(token)
    shop: FwClient.Shop = merchant.shop(shop_id)
    return merchant, shop
```

### Exception handling

Most public methods of the package may raise an exception in case something goes wrong. All exceptions thrown are guarantied to be inherited from `FwError`.

The last `except` branch should be dedicated to base error type `FwError` as a list of exceptions thrown by a method may be extended in future minor backward compatible updates.

```python
from nt_flowwow_seller_client import FwClient, FwError

async def handle_exceptions(shop: FwClient.Shop) -> None:
    try:
        await shop.get_products()
    except FwError as err:
        print(err)
```

### Response Error handling

Some requests may partially fail. It that case a corresponding method will return a list of `*RespErr` objects.

```python
from nt_flowwow_seller_client import FwClient, FwProductActiveRespErr

async def handle_resp_errors(shop: FwClient.Shop) -> None:
    resp_errors: list[FwProductActiveRespErr] = await shop.set_product_active(["1234"], False)
    for re in errors:
        print(re.raw)
```
