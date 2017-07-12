FROM python:2

WORKDIR /app

RUN apt-get update
RUN apt-get -y install apache2 php5 libapache2-mod-php5 expect php5-curl php5-mysql

RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'"
RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'"
RUN apt-get -y install mysql-server

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN pip install testfixtures # Additional library for testing

# Dependenci
# Add unprivileged testuser:testuser user
RUN echo 'testuser:$1$xyz$iqgi.17OXQwhicZgFC1OZ.:1001:1002:,,,:/home/testuser:/bin/bash' >> /etc/passwd

ENTRYPOINT "/app/tests/docker/prepare-env.sh"