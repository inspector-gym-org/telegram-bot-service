# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye AS requirements-stage

WORKDIR /tmp

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /tmp/
RUN poetry export --output requirements.txt --with=prod

FROM python:3.11-slim-bullseye AS locales-stage

RUN apt update
RUN apt install -y gettext

WORKDIR /tmp

COPY ./locale /tmp/locale
RUN find /tmp/locale -name "*.po" -exec sh -c 'msgfmt -o "${0%.po}.mo" "${0}"' {} \;

FROM python:3.11-slim-bullseye

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY --from=locales-stage /tmp/locale /code/locale

CMD [ "gunicorn", \
    "--bind", "0.0.0.0:80", \
    "--access-logfile", "-", \
    "--workers", "1", \
    "--worker-class", "uvicorn.workers.UvicornH11Worker", \
    "telegram_bot_service.main:app" ]

COPY ./telegram_bot_service /code/telegram_bot_service
