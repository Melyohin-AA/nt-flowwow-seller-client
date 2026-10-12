#!/usr/bin/env bash

set -euo pipefail

TOKEN_FILE="${PYPI_TOKEN_FILE:-$HOME/.config/pypi/token.gpg}"

if [[ ! -f "$TOKEN_FILE" ]]; then
    echo "PyPI token file not found: $TOKEN_FILE" >&2
    exit 1
fi

if ! command -v gpg >/dev/null 2>&1; then
    echo "gpg is not installed." >&2
    exit 1
fi

PYPI_TOKEN="$(gpg --quiet --decrypt "$TOKEN_FILE")"

if [[ -z "$PYPI_TOKEN" ]]; then
    echo "Failed to decrypt PyPI token." >&2
    exit 1
fi

if [[ "$PYPI_TOKEN" != pypi-* ]]; then
    echo "Decrypted value does not look like a PyPI API token." >&2
    unset PYPI_TOKEN
    exit 1
fi

export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="$PYPI_TOKEN"

unset PYPI_TOKEN

python -m twine upload dist/*

unset TWINE_PASSWORD TWINE_USERNAME
