FROM python:3

WORKDIR /app

RUN apt-get update
RUN apt-get -y install curl wget gnupg2 ca-certificates lsb-release apt-transport-https apache2 expect php-mysql zip unzip vim openssh-server

RUN wget -O /tmp/sury.gpg https://packages.sury.org/php/apt.gpg
RUN apt-key add /tmp/sury.gpg
RUN rm /tmp/sury.gpg
RUN echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/php.list
RUN apt-get update -y
RUN apt-get -y install php7.4 php7.4-fpm php7.4-mysql libapache2-mod-php7.4 libapache2-mod-fcgid php7.4-curl php7.4-gd php7.4-zip php7.4-bz2 php7.4-ssh2
RUN apt-get -y install php8.2 php8.2-fpm php8.2-mysql libapache2-mod-php8.2 libapache2-mod-fcgid php8.2-curl php8.2-gd php8.2-zip php8.2-bz2 php8.2-ssh2

RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'"
RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'"
RUN apt-get -y install default-mysql-server

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
# Additional libraries for testing
RUN pip install testfixtures coverage pexpect paramiko

# Add unprivileged testuser:testuser user
RUN echo 'testuser:$1$xyz$iqgi.17OXQwhicZgFC1OZ.:1001:1002:,,,:/home/testuser:/bin/bash' >> /etc/passwd
RUN mkdir -p /home/testuser
RUN chown testuser:users /home/testuser

RUN phpenmod ssh2

COPY tests/docker/000-default.conf /etc/apache2/sites-enabled/000-default.conf

ENTRYPOINT "/app/tests/docker/entrypoint.sh"
