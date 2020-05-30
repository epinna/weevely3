FROM python:3

WORKDIR /app

RUN apt-get update
RUN apt-get -y install apache2 php libapache2-mod-php expect php-curl php-gd php-mysql zip unzip php-zip php-bz2 vim

RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'"
RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'"
RUN apt-get -y install default-mysql-server

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN pip install testfixtures coverage # Additional library for testing

# Add unprivileged testuser:testuser user
RUN echo 'testuser:$1$xyz$iqgi.17OXQwhicZgFC1OZ.:1001:1002:,,,:/home/testuser:/bin/bash' >> /etc/passwd

ENTRYPOINT "/app/tests/docker/entrypoint.sh"
