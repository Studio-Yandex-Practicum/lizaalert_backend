FROM python:3.7.12-slim
ENV PYTHONUNBUFFERED=1

EXPOSE 8000/tcp

ENV HOME=/home/app
ENV APP_HOME=/home/app/admin
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/static
WORKDIR $APP_HOME


COPY requirements.txt .
RUN apt-get update && apt-get -y dist-upgrade
RUN apt install -y netcat
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN ["chmod", "+x", "/home/app/admin/entrypoint.sh"]