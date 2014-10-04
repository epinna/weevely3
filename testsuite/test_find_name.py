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

class FindName(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        # Create the folder tree
        self.folders_abs, self.folders_rel =  self.populate_folders()
        self.files_abs, self.files_rel = self.populate_files(
                                self.folders_abs,
                                [ 'test1', 'TEST1', 'TEST2', 'TEST3' ]
                            )

        self.run_argv = modules.loaded['find_name'].run_argv

    def tearDown(self):

        for folder in reversed(self.folders_abs):

            subprocess.check_call(
                config.cmd_env_remove_s % (self.files_abs.pop()),
                shell=True)

            subprocess.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)

    def test_find_name(self):

        # find file[0] (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ filen, '.' ]), [ './%s' % (d) for d in (self.files_rel[0], self.files_rel[1]) ])

        # find file[0] (case sensitive, recursive, not contains) -> file[0]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '-case', filen, '.' ]), [ './%s' % (self.files_rel[0]) ])

        # find the end of file[0] (case insensitive, recursive, contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(
            self.run_argv(
                [ '-contains', filen[-3:], '.' ]
            ),
            [ './%s' %d for d in (self.files_rel[0], self.files_rel[1]) ]
        )

        # find file[0] not recursive -> none
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '-no-recursion', filen, '.' ]), [ '' ])

        # find file[3] (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[3])
        self.assertItemsEqual(self.run_argv([ filen, '.' ]), [ './%s' % (self.files_rel[3]) ])

        # find file[1] with wrong rpath (case insensitive, recursive, not contains) -> none
        filep, filen = os.path.split(self.files_rel[1])
        self.assertItemsEqual(self.run_argv([ filen, self.folders_rel[-1] ]), [ '' ])

        # find file[1] with right path and no recursive. Set all the params.
        filep, filen = os.path.split(self.files_rel[1])
        self.assertItemsEqual(
            self.run_argv(
                [
                '-no-recursion',
                '-contains',
                '-case',
                filen[-3:],
                self.folders_rel[1]
                ]
            ),
        [ '%s' % (self.files_rel[1]) ])

        # find file[0] with sh vector (case insensitive, recursive, not contains) -> file[0], file[1]
        filep, filen = os.path.split(self.files_rel[0])
        self.assertItemsEqual(self.run_argv([ '-vector', 'sh_find', filen, '.' ]), [ './%s' %d for d in (self.files_rel[0], self.files_rel[1]) ] )
