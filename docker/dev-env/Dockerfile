FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        make \
        supervisor \
        gcc \ 
        cython \
        python-pip \
        python-dev 

# requirements
RUN pip install -U \
    falcon \
    gunicorn \
    requests

# test env requirements
RUN pip install -U \
    nose \
    coverage

# prepare env 
RUN mkdir -p /app && \
    mkdir -p /data && \
    mkdir -p /scripts
ADD scripts/create-env.sh /scripts/
RUN chmod +x /scripts/create-env.sh

CMD /scripts/create-env.sh

# clean temporary files 
RUN apt-get clean && rm -rf /tmp/* /var/tmp/*
 

