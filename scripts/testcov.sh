#!/usr/bin/env bash

set -euo pipefail

source venv/bin/activate
python -m pytest --cov=nt_flowwow_seller_client tests
python -m coverage html
