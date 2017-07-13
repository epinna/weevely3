#!/bin/bash
set -e

BASE_FOLDER="`python -c 'from tests import config;print(config.base_folder)'`"
AGENT="`python -c 'from tests import config;print(config.agent)'`"
URL="`python -c 'from tests import config;print(config.url)'`"
PWD="`python -c 'from tests import config;print(config.password)'`"

service apache2 start

# Generic environment setting install
mkdir -p "$BASE_FOLDER"
python ./weevely.py generate "$PWD" "$AGENT"

if [ -z "$1" ]
  then
    TEST='*'
else
    TEST="$1"
fi

python -m unittest discover ./tests/ "test_$TEST.py"