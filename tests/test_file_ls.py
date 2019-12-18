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
BASE_FOLDER="{config.base_folder}/test_file_ls/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/dir4"
chmod 0 "$BASE_FOLDER/dir1/dir2/dir3/dir4"
""".format(
config = config
), shell=True)

class FileLs(BaseTest):

    folders = [ os.path.join(config.base_folder, f) for f in (
        'test_file_ls/dir1',
        'test_file_ls/dir1/dir2',
        'test_file_ls/dir1/dir2/dir3',
        'test_file_ls/dir1/dir2/dir3/dir4',
    ) ] 

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.run_argv = modules.loaded['file_ls'].run_argv

    def test_ls(self):

        # ls [0]
        self.assertEqual(self.run_argv([ self.folders[0] ]), [ '.', '..', os.path.split(self.folders[1])[1]])

        # ls [-1]
        self.assertEqual(self.run_argv([ self.folders[-1] ]), [ ] )

        # ls [1]/.././[1]/./
        new = self.folders[1]
        self.assertEqual(self.run_argv([ '%s/.././%s/./' % (new, os.path.split(new)[-1]) ]), [ '.', '..', os.path.split(self.folders[2])[1]])

        # ls bogus
        self.assertEqual(self.run_argv([ 'bogus' ]), [ ] )

        # ls [2]/.././[2]/../
        new = self.folders[2]
        self.assertEqual(self.run_argv([ '%s/.././////////%s/../' % (new, os.path.split(new)[-1]) ]), [ '.', '..', os.path.split(self.folders[2])[1]])
