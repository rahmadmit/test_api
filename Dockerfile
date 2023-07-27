# syntax=docker/dockerfile:1
FROM python:3.10-slim

RUN pip install "poetry==1.1.11"

WORKDIR /test_api

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

#COPY poetry.lock pyproject.toml /test_api/
COPY entrypoint.sh /
RUN chmod 755 /entrypoint.sh
COPY . /test_api/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


# RUN poetry run alembic upgrade head
# RUN poetry run python -m debugpy --listen '0.0.0.0:5678' -m uvicorn --host '0.0.0.0' --port '8080' --log-level 'debug' --root-path "/api" --reload test-api:app


# COPY . .

# CMD [ "python", "./your-daemon-or-script.py" ]
ENTRYPOINT [ "/entrypoint.sh" ]