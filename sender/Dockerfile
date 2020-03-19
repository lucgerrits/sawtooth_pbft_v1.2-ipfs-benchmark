FROM ubuntu:bionic

RUN apt-get update \
 && apt-get install gnupg -y

RUN echo "deb http://repo.sawtooth.me/ubuntu/nightly bionic universe" >> /etc/apt/sources.list \
 && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA \
 || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44FC67F19B2466EA) \
 && apt-get update

RUN apt-get install -y curl

RUN curl -sL https://deb.nodesource.com/setup_13.x | bash -
RUN apt-get install -y nodejs
RUN node -v 
RUN npm -v 
RUN npm install async
RUN npm install request

RUN apt-get install -y libcurl4-openssl-dev

RUN apt-get install -y libtool


RUN apt install -y libcurl3 libcurl-openssl1.0-dev

RUN apt install -y bc

ENV PATH=$PATH:/sender

WORKDIR /sender

CMD echo "Sender ok "
