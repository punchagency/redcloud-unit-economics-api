#!/bin/bash

# Check if the virtual environment is already activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    # Activate the virtual environment
    source .venv/bin/activate
fi

export GOOGLE_APPLICATION_CREDENTIALS="gcp_config.json"
export PYTHONPATH=/app
python app/main.py