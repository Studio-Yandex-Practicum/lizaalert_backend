# pull official base image
FROM nginx:1.22-alpine
# removing the default config and copying the working
RUN rm /etc/nginx/conf.d/default.conf
# install certbot
RUN apk add --update python3 py3-pip
RUN pip install certbot-nginx
RUN mkdir /etc/letsencrypt/ && mkdir /etc/letsencrypt/live/

COPY ./services/nginx/la-testing_admin.conf /etc/nginx/conf.d/la-testing_admin.conf
COPY ./services/nginx/la-testing_api.conf /etc/nginx/conf.d/la-testing_api.conf
COPY ./services/nginx/la-testing_docs.conf /etc/nginx/conf.d/la-testing_docs.conf
COPY ./services/nginx/la-testing_swagger.conf /etc/nginx/conf.d/la-testing_swagger.conf
