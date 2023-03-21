# pull official base image
FROM nginx:1.22-alpine
# removing the default config and copying the working
RUN rm /etc/nginx/conf.d/default.conf

COPY ./services/nginx/site.conf /etc/nginx/conf.d/site.conf
