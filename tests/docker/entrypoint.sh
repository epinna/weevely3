#!/bin/bash
set -e -x

BASE_FOLDER="`python -c 'from tests import config;print(config.base_folder)'`"
AGENT="`python -c 'from tests import config;print(config.agent)'`"
URL="`python -c 'from tests import config;print(config.url)'`"
PWD="`python -c 'from tests import config;print(config.password)'`"

# Generic environment setting install
mkdir -p "$BASE_FOLDER"
find -type f -name '*.pyc' -exec rm -f {} \;
python ./weevely.py generate "$PWD" "$AGENT"

service apache2 start
service mysql start

# Grant root user to connect from network socket
mysql -u root --password=root -e "grant all privileges on *.* to 'root'@'localhost' identified by 'root'; flush privileges;"

sleep 10000
