#!/usr/bin/env bash

set -euo pipefail

source venv/bin/activate
rm -rf dist
python -m build
