from tests.base_test import BaseTest
from testfixtures import log_capture
from tests import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import datetime
import logging
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_check/"
rm -rf "$BASE_FOLDER"
mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/0333"
chmod 0333 "$BASE_FOLDER/dir1/dir2/dir3/0333"
echo -n 1 > "$BASE_FOLDER/dir1/0777"
chmod 0777 "$BASE_FOLDER/dir1/0777"
touch "$BASE_FOLDER/dir1/dir2/writable"
touch "$BASE_FOLDER/dir1/dir2/dir3/write-executable"
touch "$BASE_FOLDER/dir1/dir2/dir3/0333/0444"
chmod 0444 "$BASE_FOLDER/dir1/dir2/dir3/0333/0444"
""".format(
config = config
), shell=True)

class FileCheck(BaseTest):

    files_rel = [
        'test_file_check/dir1/0777',
        'test_file_check/dir1/dir2/writable',
        'test_file_check/dir1/dir2/dir3/write-executable',
        'test_file_check/dir1/dir2/dir3/0333/0444',
    ]
    
    folders_rel = [
        'test_file_check/dir1/',
        'test_file_check/dir1/dir2/',
        'test_file_check/dir1/dir2/dir3/',
        'test_file_check/dir1/dir2/dir3/0333/',
    ]

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)
        
        self.file_0_time = int(subprocess.check_output(
            'stat -c %%Y "%s"' % (os.path.join(config.base_folder, 'test_file_check/dir1/0777')),
            shell=True)
        )

        self.run_argv = modules.loaded['file_check'].run_argv

    def test_check(self):

        # Some check on a file just readable
        self.assertTrue(self.run_argv([ self.files_rel[3], 'exists']))
        self.assertTrue(self.run_argv([ self.files_rel[3], 'readable']))
        self.assertTrue(self.run_argv([ self.files_rel[3], 'file']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'executable']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'writable']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'dir']))

        # Some check on an unexistant file
        self.assertFalse(self.run_argv(['BOGUS', 'exists']))
        self.assertFalse(self.run_argv(['BOGUS', 'readable']))
        self.assertFalse(self.run_argv(['BOGUS', 'file']))
        self.assertFalse(self.run_argv(['BOGUS', 'executable']))
        self.assertFalse(self.run_argv(['BOGUS', 'writable']))
        self.assertFalse(self.run_argv(['BOGUS', 'dir']))

        # Some check on a folder with jsut x & w
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'exists']))
        self.assertFalse(self.run_argv([ self.folders_rel[3], 'readable']))
        self.assertFalse(self.run_argv([ self.folders_rel[3], 'file']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'executable']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'writable']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'dir']))

        # Save the human readable remote file[0] timestamp
        rdatetime = datetime.datetime.fromtimestamp(float(self.file_0_time)).strftime('%Y-%m-%d')

        self.assertTrue(self.run_argv([ self.files_rel[0], 'exists']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'readable']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'file']))
        self.assertFalse(self.run_argv([ self.files_rel[0], 'dir']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'executable']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'writable']))
        self.assertEqual(self.run_argv([ self.files_rel[0], 'size']), '1o')
        self.assertEqual(self.run_argv([ self.files_rel[0], 'md5']), 'c4ca4238a0b923820dcc509a6f75849b')
        self.assertAlmostEqual(self.run_argv([ self.files_rel[0], 'time']), self.file_0_time, delta = 20)
        self.assertEqual(self.run_argv([ self.files_rel[0], 'datetime']).split(' ')[0], rdatetime)
