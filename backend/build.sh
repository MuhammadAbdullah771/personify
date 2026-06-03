#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install "setuptools>=75.8.0,<76"
pip install -r requirements.txt
