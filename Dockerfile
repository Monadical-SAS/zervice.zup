FROM python:3.8-buster

RUN apt-get -qq update \
    && apt-get install -y grep curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir django==3

VOLUME /opt/zervice.zup
EXPOSE 8000

WORKDIR /opt/zervice.zup
ENTRYPOINT [ "./monitor.py" ]
