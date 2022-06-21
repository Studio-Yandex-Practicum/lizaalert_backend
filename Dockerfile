ARG VARIANT=3.10-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

ENV PYTHONUNBUFFERED=1

EXPOSE 8000/tcp

ENV APP_HOME=/home/app/lizaalert
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/static
RUN mkdir -p $APP_HOME/media
WORKDIR $APP_HOME

RUN apt-get -y update --no-install-recommends \
    && apt-get -y install --no-install-recommends \
    curl \
    git \
    && apt-get autoremove -y \
    && apt-get clean -y

# get poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"
