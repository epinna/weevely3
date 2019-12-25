from tests.base_test import BaseTest
from tests import config
from core import modules
from core.sessions import SessionURL
from testfixtures import log_capture
from core import messages
import logging
import os
import subprocess

class FileBzip(BaseTest):

    # Create and bzip2 binary files for the test
    binstring = [
        b'\\xe0\\xf5\\xfe\\xe2\\xbd\\x0c\\xbc\\x9b\\xa0\\x8f\\xed?\\xa1\\xe1',
        b'\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x06\\x00\\x00\\x00'
         ]
    uncompressed = [
        os.path.join(config.base_folder, 'test_file_bzip2', 'binfile0'),
        os.path.join(config.base_folder, 'test_file_bzip2', 'binfile1')
        ]
    compressed = [
        os.path.join(config.base_folder, 'test_file_bzip2', 'binfile0.bz2'),
        os.path.join(config.base_folder, 'test_file_bzip2', 'binfile1.bz2')
        ]

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_bzip2/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/"

echo -n '\\xe0\\xf5\\xfe\\xe2\\xbd\\x0c\\xbc\\x9b\\xa0\\x8f\\xed?\\xa1\\xe1' > "$BASE_FOLDER/binfile0"
echo -n '\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x06\\x00\\x00\\x00' > "$BASE_FOLDER/binfile1"

bzip2 "$BASE_FOLDER/binfile0"
bzip2 "$BASE_FOLDER/binfile1"

chown www-data: -R "$BASE_FOLDER/"

    """.format(
    config = config
    ), shell=True)

        self.run_argv = modules.loaded['file_bzip2'].run_argv
    
    def test_compress_decompress(self):

        # Decompress and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            subprocess.check_output('cat "%s"' % self.uncompressed[0], shell=True),
            self.binstring[0]
        )
    
        # Let's re-compress it, and decompress and check again
        self.assertTrue(self.run_argv([self.uncompressed[0]]))
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            subprocess.check_output('cat "%s"' % self.uncompressed[0], shell=True),
            self.binstring[0]
        )
    
        # Recompress it keeping the original file
        self.assertTrue(self.run_argv([self.uncompressed[0], '--keep']))
        # Check the existance of the original file and remove it
        subprocess.check_call('stat -c %%a "%s"' % self.uncompressed[0], shell=True)
        
        subprocess.check_call('rm "%s"' % self.uncompressed[0], shell=True)
    
        #Do the same check
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0]]));
        self.assertEqual(
            subprocess.check_output('cat "%s"' % self.uncompressed[0], shell=True),
            self.binstring[0]
        )

    def test_compress_decompress_multiple(self):
    
        for index in range(0, len(self.compressed)):
    
            # Decompress and check test file
            self.assertTrue(self.run_argv(["--decompress", self.compressed[index]]));
            self.assertEqual(
                subprocess.check_output('cat "%s"' % self.uncompressed[index], shell=True),
                self.binstring[index]
            )
    
            # Let's re-compress it, and decompress and check again
            self.assertTrue(self.run_argv([self.uncompressed[index]]))
            self.assertTrue(self.run_argv(["--decompress", self.compressed[index]]));
            self.assertEqual(
                subprocess.check_output('cat "%s"' % self.uncompressed[index], shell=True),
                self.binstring[index]
            )
    
    
    @log_capture()
    def test_already_exists(self, log_captured):
    
        # Decompress keeping it and check test file
        self.assertTrue(self.run_argv(["--decompress", self.compressed[0], '--keep']));
        self.assertEqual(
            subprocess.check_output('cat "%s"' % self.uncompressed[0], shell=True),
            self.binstring[0]
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
            subprocess.check_output('cat "%s"' % self.uncompressed[0], shell=True),
            self.binstring[0]
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
