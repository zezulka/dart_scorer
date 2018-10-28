#!/usr/bin/env bash
# This script must be run from the top-level directory.

pushd `dirname .`
python3 main.py
popd
