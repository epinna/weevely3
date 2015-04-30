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

class Curl(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

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

        self.vector_list = [
            m for m in modules.loaded['net_curl'].vectors.get_names()
            if m not in config.curl_skip_vectors
        ]

        self.run_argv = modules.loaded['net_curl'].run_argv


    def tearDown(self):

        for f in self.files:
            self.check_call(
                config.cmd_env_remove_s % (f),
                shell=True)

    def _clean_result(self, result):
        return result if not result else re.sub('[\n]|[ ]{2,}',' ', result)

    def test_sent_data(self):

        for vect in self.vector_list:

            # Simple GET
            self.assertIn(
                '[REQUEST_METHOD] => GET',
                self._clean_result(self.run_argv([ self.urls[0], '-vector', vect ])[0])
            )

            # PUT request
            self.assertIn(
                '[REQUEST_METHOD] => PUT',
                self._clean_result(self.run_argv([ self.urls[0], '-X', 'PUT', '-vector', vect ])[0])
            )

            # Add header
            self.assertIn(
                '[HTTP_X_ARBITRARY_HEADER] => bogus',
                self._clean_result(self.run_argv([ self.urls[0], '-H', 'X-Arbitrary-Header: bogus', '-vector', vect ])[0])
            )

            # Add cookie
            self.assertIn(
                '[HTTP_COOKIE] => C1=bogus;C2=bogus2',
                self._clean_result(self.run_argv([ self.urls[0], '-b', 'C1=bogus;C2=bogus2', '-vector', vect ])[0])
            )

            # POST request with data
            result = self._clean_result(self.run_argv([ self.urls[0], '--data', 'f1=data1&f2=data2', '-vector', vect ])[0])
            self.assertIn(
                '[REQUEST_METHOD] => POST',
                result
            )
            self.assertIn(
                '[f1] => data1  [f2] => data2',
                result
            )

            # GET request with URL
            result = self._clean_result(self.run_argv([ self.urls[0] + '/?f1=data1&f2=data2', '-vector', vect ])[0])
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

        for vect in self.vector_list:

            self.assertIsNone(self.run_argv([ 'http://unreachable-bogus-bogus', '-vector', vect ])[0])
            self.assertEqual(messages.module_net_curl.unexpected_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://unreachable-bogus-bogus' ])[0])
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)

    @log_capture()
    def test_filtered(self, log_captured):

        for vect in self.vector_list:

            self.assertIsNone(self.run_argv([ 'http://www.google.com:9999', '-vector', vect, '--connect-timeout', '1' ])[0])
            self.assertEqual(messages.module_net_curl.unexpected_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://www.google.com:9999', '--connect-timeout', '1' ])[0])
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)

    @log_capture()
    def test_closed(self, log_captured):

        for vect in self.vector_list:

            self.assertIsNone(self.run_argv([ 'http://localhost:43907', '-vector', vect, '--connect-timeout', '1' ])[0])
            self.assertEqual(messages.module_net_curl.unexpected_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://localhost:19999', '--connect-timeout', '1' ])[0])
        self.assertEqual(messages.module_net_curl.unexpected_response,
                         log_captured.records[-1].msg)

    def test_output_remote(self):

        for vect in self.vector_list:

            self.files.append(os.path.join(config.script_folder, 'test_%s' % vect))
            result, headers, saved = self.run_argv([ self.urls[0], '-vector', vect, '-o', self.files[-1] ])
            self.assertTrue(saved)

        self.files.append(os.path.join(config.script_folder, 'test_all'))
        result, headers, saved = self.run_argv([ self.urls[0], '-o', 'test_all' ])
        self.assertTrue(saved)

        # Check saved = None without -o
        result, headers, saved = self.run_argv([ self.urls[1] ])
        self.assertIsNone(saved)

        # Check saved = False with a wrong path
        result, headers, saved = self.run_argv([ self.urls[1], '-o', 'bogus/bogusbogus' ])
        self.assertFalse(saved)

    def test_output_local(self):

        temp_file = tempfile.NamedTemporaryFile()
        for vect in self.vector_list:

            self.files.append(temp_file.name)
            result, headers, saved = self.run_argv([ self.urls[0], '-vector', vect, '--data', 'FIND=THIS', '-o', temp_file.name, '-local' ])
            self.assertTrue(saved)
            self.assertIn('[FIND] => THIS', open(temp_file.name,'r').read())

        temp_file.truncate()
        result, headers, saved = self.run_argv([ self.urls[0], '--data', 'FIND=THIS', '-o', temp_file.name, '-local' ])
        self.assertTrue(saved)
        self.assertIn('[FIND] => THIS', open(temp_file.name,'r').read())
        temp_file.close()

        # Check saved = False with a wrong path
        result, headers, saved = self.run_argv([ self.urls[1], '-o', 'bogus/bogusbogus', '-local' ])
        self.assertFalse(saved)

    def test_all(self):

        for vect in self.vector_list:
            result, headers, saved = self.run_argv([ self.urls[1], '-vector', vect, '-i' ])
            self.assertIn('HTTP/1.1 200 OK', headers)
            self.assertIn('Content-Length: 1', headers)
            self.assertEqual(result, '1')
            self.assertIsNone(saved)

            # Check if content-length is real
            cont_len = 0
            for h in headers:
                if h.startswith('Content-Length: '):
                    cont_len = int(h[16:])
                    break

            self.assertEqual(cont_len, len(result))
