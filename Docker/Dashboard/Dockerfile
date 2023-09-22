FROM php:7.2-apache
RUN apt-get update && apt-get install -y locales locales-all
COPY script/ /site/
RUN chown -R www-data:www-data /site/
#COPY conf/000-default.conf /etc/apache2/sites-enabled/
COPY conf/apache2.conf /etc/apache2/

COPY docker/entrypoint.sh /
RUN chmod a+rx /entrypoint.sh

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/entrypoint.sh"]
