#!/bin/bash

set -ex

pip3 install -r requirements/base.txt
python3 -m uvicorn server.main:app --port 8000 --host 0.0.0.0
