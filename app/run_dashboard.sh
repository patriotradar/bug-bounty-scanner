#!/usr/bin/env bash

set -e

python3 -m pip install -r app/requirements.txt

python3 -m streamlit run app/dashboard.py \
  --server.address 0.0.0.0 \
  --server.port 8501