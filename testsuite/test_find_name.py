from testfixtures import log_capture
from testsuite.base_test import BaseTest
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import utilities
from core import messages
import core.utilities
import subprocess
import os

class FindName(BaseTest):

    def _recursive_folders(self, recursion = 4):

        folders_abs = [ config.script_folder ]

        for folder in [ utilities.randstr() for f in range(0, recursion) ]:
            folders_abs.append(os.path.join(*[ folders_abs[-1], folder ] ))

        folders_rel = [ f.replace(config.script_folder, '') for f in folders_abs[1:] ]

        return folders_abs[1:], folders_rel

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders_abs, self.folders_rel =  self._recursive_folders()

        for folder_abs in self.folders_abs:
            subprocess.check_call(
                config.cmd_env_mkdir_s % (folder_abs),
                shell=True)

        files_names = [ 'test1', 'TEST1', 'TEST2', 'TEST3' ]

        # Add a file in every folder and save paths
        self.files_abs = []
        self.files_rel = []
        for folder_abs in self.folders_abs:
            self.files_abs.append(os.path.join(folder_abs, files_names.pop(0)))
            self.files_rel.append(self.files_abs[-1].replace(config.script_folder, ''))
            subprocess.check_call(
                config.cmd_env_content_s_to_s % ('1', self.files_abs[-1]),
                shell=True)

        self.run_argv = modules.loaded['find_name'].run_argv

    def tearDown(self):

        for folder in reversed(self.folders_abs):

            subprocess.check_call(
                config.cmd_env_remove_s % (self.files_abs.pop()),
                shell=True)

            subprocess.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)


    @log_capture()
    def test_find_name(self, log_captured):

        # find file[0] (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ filen ]), [ './%s' %d for d in (self.files_rel[0], self.files_rel[1]) ])

        # find file[0] (case sensitive, recursive, not contains) -> file[0]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '--case=True', filen ]), [ './%s' % (self.files_rel[0]) ])

        # find the end of file[0] (case insensitive, recursive, contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(
            self.run_argv(
                [ '--contains=True',
                filen[-3:] ]
            ),
            [ './%s' %d for d in (self.files_rel[0], self.files_rel[1]) ] 
        )

        # find file[0] not recursive -> none
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '--recursive=False', filen ]), [ '' ])

        # find file[3] (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[3])
        self.assertItemsEqual(self.run_argv([ filen ]), [ './%s' % (self.files_rel[3]) ])

        # find file[1] with wrong rpath (case insensitive, recursive, not contains) -> none
        filep, filen = os.path.split(self.files_rel[1])
        self.assertItemsEqual(self.run_argv([ '--rpath=%s' % (self.folders_rel[-1]), filen ]), [ '' ])

        # find file[1] with right path and no recursive. Set all the params.
        filep, filen = os.path.split(self.files_rel[1])
        self.assertItemsEqual(
            self.run_argv(
                [
                '--rpath=%s' % (self.folders_rel[1]),
                '--recursive=False',
                '--contains=True',
                '--case=True',
                filen[-3:]
                ]
            ),
        [ '%s' % (self.files_rel[1]) ])

        # find file[0] with sh vector (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '--vector=sh_find', filen ]), [ './%s' %d for d in (self.files_rel[0], self.files_rel[1]) ] )
