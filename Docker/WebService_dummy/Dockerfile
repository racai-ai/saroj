FROM alpine as intermediate
LABEL stage=intermediate
RUN apk update && \
    apk add --update git
RUN git clone --depth 1 --branch master https://github.com/racai-ai/saroj.git

FROM php:7.2-apache
RUN apt-get update 
COPY --from=intermediate /saroj/WebService_dummy/ /site/
RUN chown -R www-data:www-data /site/
COPY conf/apache2.conf /etc/apache2/
COPY docker/entrypoint.sh /
RUN chmod a+rx /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/entrypoint.sh"]
