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

        # Create and gzip binary files for the test
        self.string = [
            '\\xe0\\xf5\\xfe\\xe2\\xbd\\x0c\\xbc\\x9b\\xa0\\x8f\\xed?\\xa1\\xe1',
            '\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x06\\x00\\x00\\x00'
             ]
        self.uncompressed = [
            os.path.join(config.script_folder, 'binfile0'),
            os.path.join(config.script_folder, 'binfile1')
            ]
        self.compressed = [
            os.path.join(config.script_folder, 'binfile0.gz'),
            os.path.join(config.script_folder, 'binfile1.gz')
            ]

        for index in range(0, len(self.string)):
            self.check_call(config.cmd_env_content_s_to_s % (self.string[index], self.uncompressed[index]))
            self.check_call(config.cmd_env_gzip_s % (self.uncompressed[index]))

        self.run_argv = modules.loaded['file_gzip'].run_argv

    def tearDown(self):

        for f in self.uncompressed + self.compressed:
            self.check_call(config.cmd_env_remove_s % (f))


    def test_compress_decompress(self):

        # Decompress and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.string[0]
        )

        # Let's re-compress it, and decompress and check again
        self.assertTrue(self.run_argv([self.uncompressed[0]]))
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.string[0]
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
            self.string[0]
        )

    def test_compress_decompress_multiple(self):

        for index in range(0, len(self.compressed)):

            # Decompress and check test file
            self.assertTrue(self.run_argv(["--decompress", self.compressed[index]]));
            self.assertEqual(
                self.check_output(config.cmd_env_print_repr_s % self.uncompressed[index]),
                self.string[index]
            )

            # Let's re-compress it, and decompress and check again
            self.assertTrue(self.run_argv([self.uncompressed[index]]))
            self.assertTrue(self.run_argv(["--decompress", self.compressed[index]]));
            self.assertEqual(
                self.check_output(config.cmd_env_print_repr_s % self.uncompressed[index]),
                self.string[index]
            )

    @log_capture()
    def test_already_exists(self, log_captured):

        # Decompress keeping it and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0], '--keep']));
        self.assertEqual(
            self.check_output(config.cmd_env_print_repr_s % self.uncompressed[0]),
            self.string[0]
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
            self.string[0]
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
