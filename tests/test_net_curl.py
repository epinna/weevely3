from tests.base_test import BaseTest
from testfixtures import log_capture
from tests import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import logging
import tempfile
import os
import re
import hashlib
import json
import socket

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_net_curl/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER"
chown www-data: -R "$BASE_FOLDER/"
""".format(
config = config
), shell=True)

class Curl(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.url = 'http://httpbin-inst'

        self.vector_list = modules.loaded['net_curl'].vectors.get_names()
        
        # Install pecl_http is complex and php-version dependant, so
        # let's just skip this vector test. 
        self.vector_list.remove('php_httprequest1')

        self.run_argv = modules.loaded['net_curl'].run_argv

    def _json_result(self, args):
        
        result = self.run_argv(args)[0]
        try:
            return result if not result else json.loads(result)
        except Exception as e:
            self.fail(result)

    def _headers_result(self, args):
        
        return self.run_argv(args)[1]
        
    def test_sent_data(self):

        for vect in self.vector_list:

            # Simple GET
            url = self.url + '/get'
            self.assertEqual(
                url,
                self._json_result([ url, '-vector', vect ])['url']
            )

            # PUT request
            url = self.url + '/put'
            self.assertEqual(
                url,
                self._json_result([ url, '-X', 'PUT', '-vector', vect ])['url']
            )

            # OPTIONS request - there is nothing to test OPTIONS in 
            # httpbin, but still it's an accepted VERB which returns 200 OK
            url = self.url + '/anything'
            self.assertEqual(
                b'200 OK',
                self._headers_result([ url, '-X', 'PUT', '-vector', vect ])[0][-6:]
            )

            # Add header
            url = self.url + '/headers'
            self.assertEqual(
                'value',
                self._json_result([ url, '-H', 'X-Arbitrary-Header: value', '-vector', vect ])['headers']['X-Arbitrary-Header']
            )

            # Add cookie
            url = self.url + '/cookies'
            self.assertEqual(
                {'C1': 'bogus', 'C2' : 'bogus2'},
                self._json_result([ url, '-b', 'C1=bogus;C2=bogus2', '-vector', vect ])['cookies']
            )

            # POST request with data
            url = self.url + '/post'
            result = self._json_result([ url, '--data', 'f1=data1&f2=data2', '-vector', vect ])
            self.assertEqual(
                { 'f1': 'data1', 'f2': 'data2' },
                result['form']
            )
            self.assertEqual(
                "application/x-www-form-urlencoded",
                result['headers']['Content-Type']
            )

            # POST request with binary string
            url = self.url + '/post'
            result = self._json_result([ url, '--data', 'FIELD=D\x41\x54A\x00B', '-vector', vect ])
            self.assertEqual(
                { 'FIELD': 'DATA\x00B' },
                result['form']
            )

            # Simple GET with parameters
            url = self.url + '/get?f1=data1&f2=data2'
            self.assertEqual(
                { 'f1': 'data1', 'f2': 'data2'},
                self._json_result([ url, '-vector', vect ])['args']
            )

            #  HTTPS GET to test SSL checks are disabled
            google_ip = socket.gethostbyname('www.google.com')
            self.assertIn(
                b'google',
                self.run_argv([ 'https://' + google_ip, '-vector', vect ])[0]
            )

    @log_capture()
    def test_unreachable(self, log_captured):

        for vect in self.vector_list:

            self.assertIsNone(self.run_argv([ 'http://co.uk', '-vector', vect ])[0])
            self.assertEqual(messages.module_net_curl.unexpected_response,
                             log_captured.records[-1].msg)

        self.assertIsNone(self.run_argv([ 'http://co.uk' ])[0])
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

        url = self.url + '/get'

        for vect in self.vector_list:

            result, headers, saved = self.run_argv([ url, '-vector', vect, '-o', 'test_net_curl/test_%s' % vect ])
            self.assertTrue(saved)

        result, headers, saved = self.run_argv([ url, '-o', 'test_net_curl/test_all' ])
        self.assertTrue(saved)

        # Check saved = None without -o
        result, headers, saved = self.run_argv([ url ])
        self.assertIsNone(saved)

        # Check saved = False with a wrong path
        result, headers, saved = self.run_argv([ url, '-o', 'bogus/bogusbogus' ])
        self.assertFalse(saved)

    def test_output_local(self):

        temp_file = tempfile.NamedTemporaryFile()
        for vect in self.vector_list:

            result, headers, saved = self.run_argv([ self.url + '/post', '-vector', vect, '--data', 'FIND=THIS', '-o', temp_file.name, '-local' ])
            self.assertTrue(saved)
            
            json_result = json.loads(result)
            with open(temp_file.name) as f:
                json_saved = json.load(f)
                
            self.assertEqual(json_result, json_saved)

        temp_file.close()

        # Check saved = False with a wrong path
        result, headers, saved = self.run_argv([ self.url, '-o', 'bogus/bogusbogus', '-local' ])
        self.assertFalse(saved)
