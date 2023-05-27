ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-buster as builder
ARG POETRY_VERSION=1.4.2
RUN pip install poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:${PYTHON_VERSION}-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /usr/src/app
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

EXPOSE 80
ENV DJANGO_SETTINGS_MODULE=oncall.settings
CMD ["python", "manage.py", "runserver", "--host", "0.0.0.0", "--port", "80"]