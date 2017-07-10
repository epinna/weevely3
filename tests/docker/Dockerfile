FROM python:2

WORKDIR /app

RUN apt-get update
RUN apt-get -y install apache2 php5 libapache2-mod-php5

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

ENTRYPOINT "/app/tests/docker/prepare-env.sh"