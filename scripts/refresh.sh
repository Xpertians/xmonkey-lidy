#!/bin/bash
rm -rf dist/* build/*
python3 setup.py sdist bdist_wheel > scripts/build.log
pip3 install dist/xmonkey_lidy-*-py3-none-any.whl --force-reinstall --no-deps > scripts/install.log