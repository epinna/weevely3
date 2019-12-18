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
import json
import socket


class Proxy(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.url = 'http://httpbin-inst'

        modules.loaded['net_proxy'].run_argv([ '-lhost', '0.0.0.0', '-lport', '8080' ])
        

    def run_argv(self, arguments, unquoted_args = ''):

        arguments += [ '--proxy', '127.0.0.1:8080' ]
        result = subprocess.check_output(
            'curl -s %s "%s"' % (unquoted_args, '" "'.join(arguments)),
            shell=True).strip()

        return result

    def _json_result(self, args, unquoted_args = ''):
        
        result = self.run_argv(args, unquoted_args).decode('utf-8')

        return result if not result else json.loads(result)

    def _headers_result(self, args):
        return self.run_argv(args, unquoted_args = '-sSL -D - -o /dev/null').splitlines()

    def test_all(self):

        #  HTTPS GET with no SSL check
        self.assertIn(
            b'Google',
            self.run_argv([ 'https://www.google.com', '-k' ])
        )

        #  HTTPS GET with cacert
        self.assertIn(
            b'Google',
            self.run_argv([ 'https://www.google.com' ], unquoted_args='--cacert ~/.weevely/certs/ca.crt')
        )
        
        # HTTPS without cacert
        try:
            self.run_argv([ 'https://www.google.com' ])
        except subprocess.CalledProcessError:
            pass
        else:
            self.fail("No error")

        # Simple GET
        url = self.url + '/get'
        self.assertEqual(
            url,
            self._json_result([ url ])['url']
        )

        # PUT request
        url = self.url + '/put'
        self.assertEqual(
            url,
            self._json_result([ url, '-X', 'PUT' ])['url']
        )

        # OPTIONS request - there is nothing to test OPTIONS in 
        # httpbin, but still it's an accepted VERB which returns 200 OK
        url = self.url + '/anything'
        self.assertEqual(
            b'200 OK',
            self._headers_result([ url, '-X', 'PUT' ])[0][-6:]
        )

        # Add header
        url = self.url + '/headers'
        self.assertEqual(
            'value',
            self._json_result([ url, '-H', 'X-Arbitrary-Header: value' ])['headers']['X-Arbitrary-Header']
        )

        # Add cookie
        url = self.url + '/cookies'
        self.assertEqual(
            {'C1': 'bogus', 'C2' : 'bogus2'},
            self._json_result([ url, '-b', 'C1=bogus;C2=bogus2' ])['cookies']
        )
        
        
        # POST request with data
        url = self.url + '/post'
        result = self._json_result([ url, '--data', 'f1=data1&f2=data2' ])
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
        result = self._json_result([ url ], unquoted_args="--data FIELD=$(env echo -ne 'D\\x41\\x54A\\x00B')")
        self.assertEqual(
            { 'FIELD': 'DATAB' },
            result['form']
        )

        # Simple GET with parameters
        url = self.url + '/get?f1=data1&f2=data2'
        self.assertEqual(
            { 'f1': 'data1', 'f2': 'data2' },
            self._json_result([ url ])['args']
        )

        #  HTTPS GET to test SSL checks are disabled
        google_ip = socket.gethostbyname('www.google.com')
        self.assertIn(
            b'google',
            self.run_argv([ 'https://' + google_ip, "-k" ])
        )

        # UNREACHABLE
        # This is not true depending on the used ISP, commenting it out
        #self.assertIn('Message: Bad Gateway.', self.run_argv([ 'http://co.uk:0' ]))

        # FILTERED
        self.assertIn(b'Message: Bad Gateway.', self.run_argv([ 'http://www.google.com:9999', '--connect-timeout', '1' ]))

        # CLOSED
        self.assertIn(b'Message: Bad Gateway.', self.run_argv([ 'http://localhost:9999', '--connect-timeout', '1' ]))
