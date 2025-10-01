FROM python:3

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt -y install curl wget gnupg2 ca-certificates lsb-release apt-transport-https apache2 expect php-mysql zip unzip vim openssh-server

RUN wget -qO- https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /usr/share/keyrings/sury-php.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ $(grep VERSION_CODENAME /etc/os-release | cut -d= -f2) main" > /etc/apt/sources.list.d/sury-php.list
RUN apt update && apt -y install php7.4 php7.4-fpm php7.4-mysql libapache2-mod-php7.4 libapache2-mod-fcgid php7.4-curl php7.4-gd php7.4-zip php7.4-bz2 php7.4-ssh2
RUN apt -y install php8.2 php8.2-fpm php8.2-mysql libapache2-mod-php8.2 libapache2-mod-fcgid php8.2-curl php8.2-gd php8.2-zip php8.2-bz2 php8.2-ssh2

RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'"
RUN bash -c "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'"
RUN apt -y install default-mysql-server

ENV PYTHONDONTWRITEBYTECODE=true
RUN pip install --upgrade pip

COPY . /app/
RUN pip install . --root-user-action ignore

# Additional libraries for testing
RUN pip install .[test] --root-user-action ignore

# Add unprivileged testuser:testuser user
RUN echo 'testuser:$1$xyz$iqgi.17OXQwhicZgFC1OZ.:1001:1002:,,,:/home/testuser:/bin/bash' >> /etc/passwd
RUN mkdir -p /home/testuser
RUN chown testuser:users /home/testuser

RUN phpenmod ssh2

COPY tests/docker/000-default.conf /etc/apache2/sites-enabled/000-default.conf
ENTRYPOINT ["/app/tests/docker/entrypoint.sh"]
