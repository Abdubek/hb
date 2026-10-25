#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -z "${HB_PYTHON_SOURCE:-}" ]; then
    ./scripts/build_python.sh
fi
cargo build --locked --release
