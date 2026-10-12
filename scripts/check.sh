#!/usr/bin/env bash

set -euo pipefail

echo "Performing static analysis ..."
venv/bin/python -m mypy nt_flowwow_seller_client
venv/bin/python -m mypy tests

echo "Checking for dev marks ..."
PATHS=( "nt_flowwow_seller_client" "tests" )
for path in "${PATHS[@]}"
do
    if grep -RIl "//~" "${path}"
    then
        echo -e "\033[0;91mDev Mark detected!\033[0m" >&2
        exit 1
    fi
done

echo -e "\033[0;92mOK\033[0m"
