FROM alpine as intermediate
LABEL stage=intermediate
RUN apk update && \
    apk add --update git
RUN git clone --depth 1 --branch master https://github.com/racai-ai/saroj.git

FROM php:7.4-apache
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update

# System stuff
RUN apt-get install -y tar zip unzip curl wget mc locales
RUN echo "en_US.UTF-8 UTF-8" | tee -a /etc/locale.gen
RUN locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en

# Build Python
RUN apt-get install -y gcc g++ make automake autoconf bison flex zlib1g zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libgdbm-dev uuid uuid-dev xz-utils libsqlite3-dev ncurses-dev
RUN mkdir -p /programs ; mkdir -p /programs_build/python_build
RUN cd /programs_build/python_build && wget https://github.com/python/cpython/archive/v3.11.4.tar.gz 
RUN cd /programs_build/python_build && tar -zxf v3.11.4.tar.gz 
RUN cd /programs_build/python_build/cpython-3.11.4 && ./configure --prefix=/programs/python-3.11 --enable-optimizations
RUN cd /programs_build/python_build/cpython-3.11.4 && make
RUN cd /programs_build/python_build/cpython-3.11.4 && make install

# Create venv
RUN /programs/python-3.11/bin/python3 -m venv /venv
COPY --from=intermediate /saroj/WebServiceModules/ /modules/
RUN rm -f /bin/sh ; ln -s /bin/bash /bin/sh
RUN source /venv/bin/activate && pip3 install --upgrade pip &&  pip3 install -r /modules/TextExtractor/requirements.txt && pip3 install torch --index-url https://download.pytorch.org/whl/cpu && pip3 install rwpt scikit-learn

# Setup Java
#RUN apt-get install -y default-jre
RUN apt-get install -y openjdk-17-jre-headless
COPY --from=intermediate /saroj/Rules/ /Rules/

# Setup site
COPY --from=intermediate /saroj/WebService/web/ /site/
RUN chown -R www-data:www-data /site/
COPY conf/apache2.conf /etc/apache2/
COPY conf/php.ini /usr/local/etc/php/
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid


COPY docker/entrypoint.sh /
RUN chmod a+rx /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/entrypoint.sh"]
