# pull official base image
FROM nginx:1.20.2-alpine
# removing the default config and copying the working
RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx.conf
COPY ./site.conf /etc/nginx/conf.d