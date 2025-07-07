FROM ubuntu:latest

# Installing common packages
RUN apt-get update -y && apt-get install -y software-properties-common language-pack-en-base debconf-utils curl wget

RUN ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime
RUN LC_ALL=en_US.UTF-8 add-apt-repository ppa:ondrej/php

RUN apt-get update -y && apt-get install python3 python3-pip -y
RUN apt-get update -y && apt-get install cron -y
RUN apt-get install -y iputils-ping


ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true


RUN echo "tzdata tzdata/Areas select Europe" > /tmp/preseed.txt; \
    echo "tzdata tzdata/Zones/Europe select Berlin" >> /tmp/preseed.txt; \
    debconf-set-selections /tmp/preseed.txt && \
    apt-get update && \
    apt-get install -y tzdata

RUN mkdir /home/labDirectory
RUN mkdir /home/.evaluationScripts
WORKDIR /home/labDirectory
# EXPOSE 30001
ENTRYPOINT ["/home/.evaluationScripts/server.sh"]


#CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done" ]