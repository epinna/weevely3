#!/bin/bash
set -e -x

BASE_FOLDER="`python -c 'from tests import config;print(config.base_folder)'`"
AGENT="`python -c 'from tests import config;print(config.agent)'`"
URL="`python -c 'from tests import config;print(config.url)'`"
PWD="`python -c 'from tests import config;print(config.password)'`"

# Generic environment setting install
mkdir -p "$BASE_FOLDER"
find -type f -name '*.pyc' -exec rm -f {} \;
python ./weevely.py generate -obfuscator obfusc1_php "$PWD" "$AGENT"
python ./weevely.py generate "$PWD" "$BASE_FOLDER"agent.phar

a2enmod actions fcgid alias proxy_fcgi

update-alternatives --set php /usr/bin/php7.4

service php7.4-fpm start
service php8.2-fpm start
service ssh start
service apache2 start
service mariadb start

# Grant root user to connect from network socket
mysql -u root --password=root -e "grant all privileges on *.* to 'root'@'localhost' identified by 'root'; flush privileges;"

sleep 10000
