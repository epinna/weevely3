from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os

class FileCd(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.folders, folders_rel = self.populate_folders()

        # Change mode of the last folder to 0
        self.check_call(
            config.cmd_env_chmod_s_s % ('0', self.folders[-1]),
            shell=True)

        self.run_argv = modules.loaded['file_cd'].run_argv

    def tearDown(self):

        # Reset mode of the last folder to 777
        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', self.folders[-1]),
            shell=True)

        for folder in reversed(self.folders):
            self.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)


    @log_capture()
    def test_cwd(self, log_captured):

        # cd [0]
        new = self.folders[0]
        self.run_argv([ new ])
        self.assertEquals(new, self.session['file_cd']['results']['cwd'])

        # cd [-1]
        new = self.folders[-1]
        self.run_argv([ new ])
        self.assertEquals(self.folders[0], self.session['file_cd']['results']['cwd'])
        self.assertEqual(
            messages.module_file_cd.failed_directory_change_to_s % new,
            log_captured.records[-1].msg
        )

        # new [1]/.././[1]/./
        new = self.folders[1]
        self.run_argv([ '%s/.././%s/./' % (new, os.path.split(new)[-1]) ])
        self.assertEquals(new, self.session['file_cd']['results']['cwd'])

        # new bogus
        new = 'bogus'
        self.run_argv([ new ])
        self.assertEquals(self.folders[1], self.session['file_cd']['results']['cwd'])
        self.assertEqual(
            messages.module_file_cd.failed_directory_change_to_s % new,
            log_captured.records[-1].msg
        )

        # new [2]/.././[2]/../
        new = self.folders[2]
        self.run_argv([ '%s/.././////////%s/../' % (new, os.path.split(new)[-1]) ])
        self.assertEquals(self.folders[1], self.session['file_cd']['results']['cwd'])
