#!/usr/bin/env bash

set -euo pipefail

source venv/bin/activate
cd sphinx
make html
cd ..
rm -rf docs
mv sphinx/build/html docs
