from testsuite.base_test import BaseTest
from testsuite import config
from core import sessions
from core import modules
from core import utilities
import core.utilities
import subprocess
import os

class FileCd(BaseTest):

    def _recursive_folders(self, recursion = 4):

        folders = [ config.script_folder ]

        for folder in [ utilities.randstr() for f in range(0, recursion) ]:
            folders.append(os.path.join(*[ folders[-1], folder ] ))

        return folders[1:]

    def setUp(self):
        session = sessions.start_session_by_url(self.url, self.password, volatile = True)
        modules.load_modules(session)

        self.folders =  self._recursive_folders()
        for folder in self.folders:
            subprocess.check_call(
                config.cmd_env_mkdir_s % (folder),
                shell=True)


        self.run_argv = modules.loaded['file_check'].run_argv

    def tearDown(self):
        for folder in reversed(self.folders):
            subprocess.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)


    def test_cwd(self):
        pass
