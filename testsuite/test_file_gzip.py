from testsuite.base_test import BaseTest
from core import modules
from core.sessions import SessionURL
from testfixtures import log_capture
from core import messages
import logging
import config
import os

class FileGzip(BaseTest):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        # Create and gzip a binary file for the test
        self.binary_string = '\\xe0\\xf5\\xfe\\xe2\\xbd\\x0c\\xbc\\x9b\\xa0\\x8f\\xed?\\xa1\\xe1'
        self.uncompressed = [ os.path.join(config.script_folder, 'binfile') ]
        self.compressed = [ os.path.join(config.script_folder, 'binfile.gz') ]

        self.check_call(config.cmd_env_content_s_to_s % (self.binary_string, self.uncompressed[0]))
        self.check_call(config.cmd_env_gzip_s % (self.uncompressed[0]))

        self.run_argv = modules.loaded['file_gzip'].run_argv

    def tearDown(self):

        for f in self.uncompressed + self.compressed:
            self.check_call(config.cmd_env_remove_s % (f))


    def test_compress_decompress(self):

        # Decompress and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.binary_string
        )

        # Let's re-compress it, and decompress and check again
        self.assertTrue(self.run_argv([self.uncompressed[0]]))
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.binary_string
        )

        # Recompress it keeping the original file
        self.assertTrue(self.run_argv([self.uncompressed[0], '--keep']))
        # Check the existance of the original file and remove it
        self.check_call(config.cmd_env_stat_permissions_s % self.uncompressed[0])
        self.check_call(config.cmd_env_remove_s % self.uncompressed[0])

        # Do the same check
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.binary_string
        )


    @log_capture()
    def test_already_exists(self, log_captured):

        # Decompress keeping it and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0], '--keep']));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.binary_string
        )

        # Do it again and trigger that the file decompressed already exists
        self.assertIsNone(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(log_captured.records[-1].msg,
                         "File '%s' already exists, skipping decompressing" % self.uncompressed[0])

        # Compress and trigger that the file compressed already exists
        self.assertIsNone(self.run_argv([self.uncompressed[0]]));
        self.assertEqual(log_captured.records[-1].msg,
                         "File '%s' already exists, skipping compressing" % self.compressed[0])

    @log_capture()
    def test_wrong_ext(self, log_captured):

        # Decompress it and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.binary_string
        )

        # Decompress the decompressed, wrong ext
        self.assertIsNone(self.run_argv(["--decompress", self.uncompressed[0]]));
        self.assertEqual(log_captured.records[-1].msg,
                         "Unknown suffix, skipping decompressing")

    @log_capture()
    def test_unexistant(self, log_captured):

        # Decompress it and check test file
        self.assertIsNone(self.run_argv(["--decompress", 'bogus']));
        self.assertEqual(log_captured.records[-1].msg,
                         "Skipping file '%s', check existance and permission" % 'bogus')
