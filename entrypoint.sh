#!/usr/bin/env bash

sleep 5
alembic upgrade head
poetry run python -m uvicorn --host '0.0.0.0' --port '8080' --workers '1' --reload test_api.main:app