from testfixtures import log_capture
from tests.base_test import BaseTest
from tests import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_cd/"
rm -rf "$BASE_FOLDER"
mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/dir4"
chmod 0 "$BASE_FOLDER/dir1/dir2/dir3/dir4"
""".format(
config = config
), shell=True)

class FileCd(BaseTest):

    folders = [ os.path.join(config.base_folder, f) for f in (
        'test_file_cd/dir1',
        'test_file_cd/dir1/dir2',
        'test_file_cd/dir1/dir2/dir3',
        'test_file_cd/dir1/dir2/dir3/dir4',
    ) ] 

    def setUp(self):
        self.session = SessionURL(
            self.url,
            self.password,
            volatile = True
        )

        modules.load_modules(self.session)

        self.run_argv = modules.loaded['file_cd'].run_argv

    @log_capture()
    def test_cwd(self, log_captured):

        # cd [0]
        new = self.folders[0]
        self.run_argv([ new ])
        self.assertEqual(new, self.session['file_cd']['results']['cwd'])

        # cd [-1]
        new = self.folders[-1]
        self.run_argv([ new ])
        self.assertEqual(self.folders[0], self.session['file_cd']['results']['cwd'])
        self.assertEqual(
            messages.module_file_cd.failed_directory_change_to_s % new,
            log_captured.records[-1].msg
        )

        # new [1]/.././[1]/./
        new = self.folders[1]
        self.run_argv([ '%s/.././%s/./' % (new, os.path.split(new)[-1]) ])
        self.assertEqual(new, self.session['file_cd']['results']['cwd'])

        # new bogus
        new = 'bogus'
        self.run_argv([ new ])
        self.assertEqual(self.folders[1], self.session['file_cd']['results']['cwd'])
        self.assertEqual(
            messages.module_file_cd.failed_directory_change_to_s % new,
            log_captured.records[-1].msg
        )

        # new [2]/.././[2]/../
        new = self.folders[2]
        self.run_argv([ '%s/.././////////%s/../' % (new, os.path.split(new)[-1]) ])
        self.assertEqual(self.folders[1], self.session['file_cd']['results']['cwd'])
