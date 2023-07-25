FROM alpine as intermediate
LABEL stage=intermediate
RUN apk update && \
    apk add --update git
RUN git clone --depth 1 --branch master https://github.com/racai-ai/saroj.git

FROM php:7.2-apache
RUN apt-get update 
COPY --from=intermediate /saroj/tests/ /site/
RUN chown -R www-data:www-data /site/
COPY docker/entrypoint.sh /
RUN chmod a+rx /entrypoint.sh

ARG WSURL
ENV WSURL=$WSURL

CMD ["/entrypoint.sh"]
