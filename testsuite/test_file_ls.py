from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import utilities
from core import messages
import core.utilities
import subprocess
import os

class FileLs(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders, folders_rel = self.populate_folders()

        # Change mode of the last folder to 0
        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('0', self.folders[-1]),
            shell=True)

        self.run_argv = modules.loaded['file_ls'].run_argv

    def tearDown(self):

        # Reset mode of the last folder to 777
        subprocess.check_call(
            config.cmd_env_chmod_s_s % ('777', self.folders[-1]),
            shell=True)

        for folder in reversed(self.folders):
            subprocess.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)


    @log_capture()
    def test_ls(self, log_captured):

        # ls [0]
        self.assertEquals(self.run_argv([ self.folders[0] ]), [ os.path.split(self.folders[1])[1]])

        # ls [-1]
        self.assertEquals(self.run_argv([ self.folders[-1] ]), None )

        # ls [1]/.././[1]/./
        new = self.folders[1]
        self.assertEquals(self.run_argv([ '%s/.././%s/./' % (new, os.path.split(new)[-1]) ]), [ os.path.split(self.folders[2])[1]])

        # ls bogus
        self.assertEquals(self.run_argv([ 'bogus' ]), None )

        # ls [2]/.././[2]/../
        new = self.folders[2]
        self.assertEquals(self.run_argv([ '%s/.././////////%s/../' % (new, os.path.split(new)[-1]) ]), [ os.path.split(self.folders[2])[1]])
