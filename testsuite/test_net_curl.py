from testsuite.base_test import BaseTest
from testfixtures import log_capture
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import logging
import os
import re

class Curl(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        fname = 'check.php'
        self.file_check = os.path.join(config.script_folder, fname)
        subprocess.check_call(
            config.cmd_env_content_s_to_s % ('<?php print_r(\$_SERVER);print_r(\$_REQUEST); ?>', self.file_check),
            shell=True)

        self.url_check = os.path.sep.join([
                            config.script_folder_url.rstrip('/'),
                            fname]
                            )

        self.run_argv = modules.loaded['net_curl'].run_argv


    def tearDown(self):
        subprocess.check_call(
            config.cmd_env_remove_s % (self.file_check),
            shell=True)

    def _clean_result(self, result):
        return result if not result else re.sub('[\n]|[ ]{2,}',' ', result)

    def test_curl(self):

        for vect in modules.loaded['net_curl'].vectors.get_names():

            # Simple GET
            self.assertIn(
                '[REQUEST_METHOD] => GET',
                self._clean_result(self.run_argv([ self.url_check, '-vector', vect ]))
            )

            # PUT request
            self.assertIn(
                '[REQUEST_METHOD] => PUT',
                self._clean_result(self.run_argv([ self.url_check, '-X', 'PUT', '-vector', vect ]))
            )

            # Add header
            self.assertIn(
                '[HTTP_X_ARBITRARY_HEADER] => bogus',
                self._clean_result(self.run_argv([ self.url_check, '-H', 'X-Arbitrary-Header: bogus', '-vector', vect ]))
            )

            # Add cookie
            self.assertIn(
                '[HTTP_COOKIE] => C1=bogus;C2=bogus2',
                self._clean_result(self.run_argv([ self.url_check, '-b', 'C1=bogus;C2=bogus2', '-vector', vect ]))
            )

            # POST request with data
            result = self._clean_result(self.run_argv([ self.url_check, '--data', 'f1=data1&f2=data2', '-vector', vect ]))
            self.assertIn(
                '[REQUEST_METHOD] => POST',
                result
            )
            self.assertIn(
                '[f1] => data1  [f2] => data2',
                result
            )

            # GET request with URL
            result = self._clean_result(self.run_argv([ self.url_check + '/?f1=data1&f2=data2', '-vector', vect ]))
            self.assertIn(
                '[REQUEST_METHOD] => GET',
                result
            )
            self.assertIn(
                '[f1] => data1  [f2] => data2',
                result
            )

    @log_capture()
    def test_unreachable(self, log_captured):

        for vect in modules.loaded['net_curl'].vectors.get_names():

            self.assertIsNone(self.run_argv([ 'http://unreachable-bogus-bogus', '-vector', vect ]))
            self.assertEqual(messages.module_net_curl.empty_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://unreachable-bogus-bogus' ]))
        self.assertEqual(messages.module_net_curl.empty_response,
                         log_captured.records[-1].msg)

    @log_capture()
    def test_filtered(self, log_captured):

        for vect in modules.loaded['net_curl'].vectors.get_names():

            self.assertIsNone(self.run_argv([ 'http://www.google.com:9999', '-vector', vect, '--connect-timeout', '1' ]))
            self.assertEqual(messages.module_net_curl.empty_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://www.google.com:9999', '--connect-timeout', '1' ]))
        self.assertEqual(messages.module_net_curl.empty_response,
                         log_captured.records[-1].msg)
