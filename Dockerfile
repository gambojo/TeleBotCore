FROM python:3.11-slim

ARG USERNAME=bot
ARG GROUPNAME=bot
ARG DATADIR=data
ARG WORKDIR=/app
ARG MAINFILE=main.py

LABEL author="github.com/gambojo"
LABEL version=1.0.0

RUN apt-get update && \
    apt-get install -y \
        postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install \
        --no-cache-dir \
        -r requirements.txt

WORKDIR $WORKDIR
COPY . .

RUN mkdir -p $DATADIR && \
    groupadd -r $GROUPNAME && \
    useradd -r -g $GROUPNAME $USERNAME && \
    chown -R $USERNAME:$GROUPNAME $WORKDIR

USER $USERNAME
CMD ["python", "$MAINFILE"]
