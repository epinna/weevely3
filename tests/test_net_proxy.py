from tests.base_test import BaseTest
from tests import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import logging
import tempfile
import os
import re
import time

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_net_proxy/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER"
echo -n '<?php print_r($_SERVER);print_r($_REQUEST); ?>' > "$BASE_FOLDER/check1.php"
echo -n '1' > "$BASE_FOLDER/check2.html"
chown www-data: -R "$BASE_FOLDER/"
""".format(
config = config
), shell=True)

class Proxy(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.checkurl = 'http://localhost/test_net_proxy/check1.php'

        modules.loaded['net_proxy'].run_argv([ '-lhost', '0.0.0.0', '-lport', '8080' ])
        

    def run_argv(self, arguments):

        arguments += [ '--proxy', '127.0.0.1:8080' ]
        result = subprocess.check_output(
            'curl -s --cacert ~/.weevely/certs/ca.crt "%s"' % ('" "'.join(arguments)),
            shell=True).strip()

        return result


    def _clean_result(self, result):
        return result if not result else re.sub('[\n]|[ ]{2,}',' ', result)

    def test_all(self):


        # Simple HTTPS GET with no SSL check
        self.assertIn(
            'Google',
            self._clean_result(self.run_argv([ 'https://www.google.com', '-k' ]))
        )

        # Simple HTTPS GET with cacert
        self.assertIn(
            'Google',
            self._clean_result(self.run_argv([ 'https://www.google.com' ]))
        )

        # Simple GET
        self.assertIn(
            '[REQUEST_METHOD] => GET',
            self._clean_result(self.run_argv([ self.checkurl ]))
        )

        # PUT request
        self.assertIn(
            '[REQUEST_METHOD] => PUT',
            self._clean_result(self.run_argv([ self.checkurl, '-X', 'PUT' ]))
        )

        # Add header
        self.assertIn(
            '[HTTP_X_ARBITRARY_HEADER] => bogus',
            self._clean_result(self.run_argv([ '-H', 'X-Arbitrary-Header: bogus', self.checkurl ]))
        )


        # Add cookie
        self.assertIn(
            '[HTTP_COOKIE] => C1=bogus;C2=bogus2',
            self._clean_result(self.run_argv([ self.checkurl, '-b', 'C1=bogus;C2=bogus2']))
        )

        # POST request with data
        result = self._clean_result(self.run_argv([ self.checkurl, '--data', 'f1=data1&f2=data2' ]))
        self.assertIn(
            '[REQUEST_METHOD] => POST',
            result
        )
        self.assertIn(
            '[f1] => data1  [f2] => data2',
            result
        )

        # GET request with URL
        result = self._clean_result(self.run_argv([ self.checkurl + '/?f1=data1&f2=data2' ]))
        self.assertIn(
            '[REQUEST_METHOD] => GET',
            result
        )
        self.assertIn(
            '[f1] => data1  [f2] => data2',
            result
        )

        # UNREACHABLE
        self.assertIn('Message: Bad Gateway.', self.run_argv([ 'http://co.uk:0' ]))

        # FILTERED
        self.assertIn('Message: Bad Gateway.', self.run_argv([ 'http://www.google.com:9999', '--connect-timeout', '1' ]))

        # CLOSED
        self.assertIn('Message: Bad Gateway.', self.run_argv([ 'http://localhost:9999', '--connect-timeout', '1' ]))
