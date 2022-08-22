FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

EXPOSE 8000/tcp

RUN apt-get --yes update --no-install-recommends \
    && apt-get install --yes --quiet --no-install-recommends \
    curl \
    git \
    && apt-get autoremove --yes \
    && apt-get clean --yes

# get poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /lizaalert/

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && rm -rf /root/.cache/pypoetry/cache \
    && rm -rf /root/.cache/pypoetry/artifacts

COPY pytest.ini .
COPY setup.cfg .
COPY conftest.py .
COPY tests/ .
COPY lizaalert-backend .

CMD ["gunicorn", "-c", "/lizaalert/gunicorn_conf.py", "settings.wsgi"]