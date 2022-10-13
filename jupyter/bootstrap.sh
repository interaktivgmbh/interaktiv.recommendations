#!/usr/bin/env bash

[ ! -d "./.venv/" ] && virtualenv -p python3.8 ./.venv/
./.venv/bin/pip install -r ./requirements.txt
