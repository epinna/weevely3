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

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_net_curl/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER"
echo -n '<?php print_r($_SERVER);print_r($_REQUEST); ?>' > "$BASE_FOLDER/check1.php"
echo -n '1' > "$BASE_FOLDER/check2.html"
echo -n '<?php print(md5($_REQUEST['data'])); ?>' > "$BASE_FOLDER/check3.php"
chown www-data: -R "$BASE_FOLDER/"
""".format(
config = config
), shell=True)

class Curl(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.urls = [
            config.base_url + '/test_net_curl/check1.php',
            config.base_url + '/test_net_curl/check2.html',
            config.base_url + '/test_net_curl/check3.php',
        ]

        self.vector_list = modules.loaded['net_curl'].vectors.get_names()
        
        # Install pecl_http is complex and php-version dependant, so
        # let's just skip this vector test. 
        self.vector_list.remove('php_httprequest1')

        self.run_argv = modules.loaded['net_curl'].run_argv

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

            # OPTIONS request
            self.assertIn(
                '[REQUEST_METHOD] => OPTIONS',
                self._clean_result(self.run_argv([ self.urls[0], '-X', 'OPTIONS', '-vector', vect ])[0])
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

            # POST request with binary string
            result = self._clean_result(self.run_argv([ self.urls[0], '--data', 'FIELD=D\x41\x54A\x00B', '-vector', vect ])[0])
            self.assertIn(
                '[REQUEST_METHOD] => POST',
                result
            )
            self.assertIn(
                '[FIELD] => DATA',
                result
            )

            # POST request with binary data
            bindata = '\xbe\xee\xc8d\xf8d\x08\xe4'
            result = self.run_argv([ self.urls[2], '--data', 'data=' + bindata, '-vector', vect ])[0]
            self.assertEqual(
                hashlib.md5(bindata).hexdigest(),
                result,
                vect
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

        for vect in self.vector_list:

            result, headers, saved = self.run_argv([ self.urls[0], '-vector', vect, '-o', 'test_net_curl/test_%s' % vect ])
            self.assertTrue(saved)

        result, headers, saved = self.run_argv([ self.urls[0], '-o', 'test_net_curl/test_all' ])
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
