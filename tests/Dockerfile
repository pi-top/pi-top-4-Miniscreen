FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update

RUN  apt install -y \
    python3 \
    python3-pip \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev

RUN rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt --extra-index-url=https://packagecloud.io/pi-top/pypi/pypi/simple

RUN rm -f /tmp/requirements.txt

COPY scripts/run.sh /

WORKDIR /src

ENTRYPOINT [ "/run.sh" ]
