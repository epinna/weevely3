from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import utilities
from core import messages
import core.utilities
import subprocess
import tempfile
import urlparse
import os

class UploadWeb(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders_abs, self.folders_rel =  self.populate_folders()

        # Change mode of the folders [1:3] to -r-xr-xr-x 0555 read & execute
        for fold in self.folders_abs:
            subprocess.check_call(
                config.cmd_env_chmod_s_s % ('0111', self.folders_abs[0]),
                shell=True)

        self.filenames = []



        self.run_argv = modules.loaded['file_upload2web'].run_argv

    def tearDown(self):

        # Reset recursively all the permissions to 0777
        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('-R 0777', self.folders_abs[0]),
            shell=True)

        for folder in reversed(self.folders_abs):

            subprocess.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)

        for f in self.filenames:
            subprocess.check_call(
                config.cmd_env_remove_s % (os.path.join(config.script_folder, f)),
                shell=True)

    def test_file_uploadweb(self):

        # Upload lfile with a specific path
        temp_file = tempfile.NamedTemporaryFile()
        self.filenames.append('f1')
        rurl = os.path.join(config.script_folder_url, 'f1')
        rpath = urlparse.urljoin(config.script_folder, 'f1')
        self.assertTrue(
            self.run_argv([ temp_file.name, rpath ]),
            [ [ rpath, rurl ] ]
            )
        temp_file.close()

        # Upload lfile guessing first writable path
        temp_file = tempfile.NamedTemporaryFile()
        self.filenames.append('f2')
        rurl = os.path.join(config.script_folder_url, 'f2')
        rpath = urlparse.urljoin(config.script_folder, 'f2')
        self.assertTrue(
            self.run_argv([ temp_file.name ]),
            [ [ rpath, rurl ] ]
            )
        temp_file.close()
