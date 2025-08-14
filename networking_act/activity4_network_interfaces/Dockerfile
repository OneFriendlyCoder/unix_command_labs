FROM ubuntu:latest

# noninteractive and locale up front so installs are non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true
ENV LC_ALL=en_US.UTF-8

# Installing common packages (no-recommends reduces image size)
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends software-properties-common language-pack-en-base debconf-utils curl wget ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

# add the PPA (software-properties-common provides add-apt-repository)
RUN add-apt-repository -y ppa:ondrej/php

# install python, pip, cron, iputils-ping (combine and cleanup)
RUN apt-get update --allow-releaseinfo-change || apt-get update -o Acquire::AllowReleaseInfoChange=true \
 && apt-get install -y --no-install-recommends python3 python3-pip cron iputils-ping \
 && rm -rf /var/lib/apt/lists/*

# Preseed tzdata and install tzdata + iproute2 (allow releaseinfo change again)
RUN echo "tzdata tzdata/Areas select Europe" > /tmp/preseed.txt \
 && echo "tzdata tzdata/Zones/Europe select Berlin" >> /tmp/preseed.txt \
 && debconf-set-selections /tmp/preseed.txt \
 && apt-get update --allow-releaseinfo-change || apt-get update -o Acquire::AllowReleaseInfoChange=true \
 && apt-get install -y --no-install-recommends tzdata iproute2 \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /tmp/preseed.txt

RUN mkdir -p /home/labDirectory
RUN mkdir -p /home/.evaluationScripts
WORKDIR /home/labDirectory

CMD ["/bin/bash", "-c", "ip -4 addr | grep 'inet ' | awk '{print $2}' > /home/.evaluationScripts/correct_ipv4_addresses.txt; while :; do sleep 10; done"]