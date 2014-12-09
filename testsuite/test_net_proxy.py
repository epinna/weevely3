from testsuite.base_test import BaseTest
from testfixtures import log_capture
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import logging
import tempfile
import os
import re

class Proxy(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        modules.loaded['net_proxy'].run_argv([ ])

        fnames = [ 'check1.php', 'check2.html' ]

        self.files = [
            os.path.join(config.script_folder, fnames[0]),
            os.path.join(config.script_folder, fnames[1])
            ]

        self.check_call(
            config.cmd_env_content_s_to_s % ('<?php print_r(\$_SERVER);print_r(\$_REQUEST); ?>', self.files[0]),
            shell=True)

        self.check_call(
            config.cmd_env_content_s_to_s % ('1', self.files[1]),
            shell=True)

        self.urls = [
            os.path.sep.join([
                config.script_folder_url.rstrip('/'),
                fnames[0]]
            ),
            os.path.sep.join([
                config.script_folder_url.rstrip('/'),
                fnames[1]]
            )
        ]

    def run_argv(self, arguments):

        arguments += [ '--proxy', 'localhost:8080' ]
        result = subprocess.check_output(
            config.cmd_env_curl_s % ('" "'.join(arguments)),
            shell=True).strip()

        return result if result != 'None' else None


    def tearDown(self):

        for f in self.files:
            self.check_call(
                config.cmd_env_remove_s % (f),
                shell=True)

    def _clean_result(self, result):
        return result if not result else re.sub('[\n]|[ ]{2,}',' ', result)

    @log_capture()
    def test_all(self, log_captured):

        # Simple GET
        self.assertIn(
            '[REQUEST_METHOD] => GET',
            self._clean_result(self.run_argv([ self.urls[0] ]))
        )

        # PUT request
        self.assertIn(
            '[REQUEST_METHOD] => PUT',
            self._clean_result(self.run_argv([ self.urls[0], '-X', 'PUT' ]))
        )

        # Add header
        self.assertIn(
            '[HTTP_X_ARBITRARY_HEADER] => bogus',
            self._clean_result(self.run_argv([ '-H', 'X-Arbitrary-Header: bogus', self.urls[0] ]))
        )


        # Add cookie
        self.assertIn(
            '[HTTP_COOKIE] => C1=bogus;C2=bogus2',
            self._clean_result(self.run_argv([ self.urls[0], '-b', 'C1=bogus;C2=bogus2']))
        )

        # POST request with data
        result = self._clean_result(self.run_argv([ self.urls[0], '--data', 'f1=data1&f2=data2' ]))
        self.assertIn(
            '[REQUEST_METHOD] => POST',
            result
        )
        self.assertIn(
            '[f1] => data1  [f2] => data2',
            result
        )

        # GET request with URL
        result = self._clean_result(self.run_argv([ self.urls[0] + '/?f1=data1&f2=data2' ]))
        self.assertIn(
            '[REQUEST_METHOD] => GET',
            result
        )
        self.assertIn(
            '[f1] => data1  [f2] => data2',
            result
        )

        # UNREACHABLE

        self.assertIsNone(self.run_argv([ 'http://unreachable-bogus-bogus' ]))
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)

        # FILTERED
        self.assertIsNone(self.run_argv([ 'http://www.google.com:9999', '--connect-timeout', '1' ]))
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)

        # CLOSED
        self.assertIsNone(self.run_argv([ 'http://localhost:9999', '--connect-timeout', '1' ]))
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)
