from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os

class FindPerms(BaseFilesystem):

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
                                [ 'executable', 'writable', 'write-executable', 'readable' ]
                            )

        # Change mode of the first file to ---x--x--x 0111 execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0111', self.files_abs[0]),
            shell=True)

        # Change mode of the second file to --w--w--w- 0222 write
        self.check_call(
            config.cmd_env_chmod_s_s % ('0222', self.files_abs[1]),
            shell=True)

        # Change mode of the third file to --wx-wx-wx 0333 write & execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0333', self.files_abs[2]),
            shell=True)

        # Change mode of the forth file to -r--r--r-- 0444 read
        self.check_call(
            config.cmd_env_chmod_s_s % ('0444', self.files_abs[3]),
            shell=True)

        # Change mode of the first folder to -rwxrwxrwx 0777 read, write, & execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', self.folders_abs[1]),
            shell=True)

        self.run_argv = modules.loaded['file_find'].run_argv

    def tearDown(self):

        # Reset recursively all the permissions to 0777
        self.check_call(
            config.cmd_env_chmod_s_s % ('-R 0777', self.folders_abs[0]),
            shell=True)

        for folder in reversed(self.folders_abs):

            self.check_call(
                config.cmd_env_remove_s % (self.files_abs.pop()),
                shell=True)

            self.check_call(
                config.cmd_env_rmdir_s % (folder),
                shell=True)

    def test_file_find_php(self):

        # find first writable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-writable', '-quit', self.folders_rel[0] ]), [ self.folders_rel[1] ])

        # find first writable file from folder[0]
        self.assertItemsEqual(self.run_argv([ '-writable', '-quit', self.folders_rel[0], '-ftype', 'f' ]), [ self.files_rel[1] ])

        # find all executable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-executable', self.folders_rel[0] ]), self.folders_rel + [  self.files_rel[2], self.files_rel[0] ] )

        # find all executable starting from folder[0] that matches the regexp 'te-ex' -> folder[2]
        self.assertItemsEqual(self.run_argv([ '-executable', self.folders_rel[0], 'te-ex' ]), [ self.files_rel[2] ])

        # find all starting from folder[0] that matches the regexp 'TE-EX' -> folder[2]
        self.assertItemsEqual(self.run_argv([ self.folders_rel[0], 'TE-EX' ]), [ self.files_rel[2] ])

        # find all  starting from folder[0] that matches the regexp 'TE-EX' and case sensitive -> []
        self.assertItemsEqual(self.run_argv([ '-case', self.folders_rel[0], 'TE-EX' ]), [ '' ])

        # find all readable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-readable', self.folders_rel[0] ]), self.folders_rel + [  self.files_rel[3] ] )

        # find all readable starting from folder[0] with a wrong regex -> none
        self.assertItemsEqual(self.run_argv([ '-readable', self.folders_rel[0], 'bogus' ]), [ '' ] )

        # find readable starting from folder[0] with no recursion
        self.assertItemsEqual(self.run_argv([ '-readable', '-no-recursion', self.folders_rel[0] ]), self.folders_rel[:2] )

        # test bogus path
        self.assertEqual(self.run_argv([ '-readable', 'bogus' ]), [''] )


    def test_file_find_sh(self):

        # find first writable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-writable', '-vector', 'sh_find', '-quit', self.folders_rel[0] ]), [ self.folders_rel[1] ])

        # find all executable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-executable', '-vector', 'sh_find', self.folders_rel[0] ]), self.folders_rel + [  self.files_rel[2], self.files_rel[0] ] )

        # find all executable starting from folder[0] that matches the regexp '-' -> folder[2]
        self.assertItemsEqual(self.run_argv([ '-executable', '-vector', 'sh_find', self.folders_rel[0], 'te-ex' ]), [ self.files_rel[2] ])

        # find all starting from folder[0] that matches the regexp 'TE-EX' -> folder[2]
        self.assertItemsEqual(self.run_argv([ '-vector', 'sh_find', self.folders_rel[0], 'TE-EX' ]), [ self.files_rel[2] ])

        # find all  starting from folder[0] that matches the regexp 'TE-EX' and case sensitive -> []
        self.assertItemsEqual(self.run_argv([ '-case', '-vector', 'sh_find', self.folders_rel[0], 'TE-EX' ]), [ '' ])

        # find all readable starting from folder[0]
        self.assertItemsEqual(self.run_argv([ '-readable', '-vector', 'sh_find', self.folders_rel[0] ]), self.folders_rel + [  self.files_rel[3] ] )

        # find all readable starting from folder[0] with a wrong regex -> none
        self.assertItemsEqual(self.run_argv([ '-readable', self.folders_rel[0], 'bogus' ]), [ '' ] )

        # find readable starting from folder[0] with no recursion
        self.assertItemsEqual(self.run_argv([ '-readable', '-vector', 'sh_find', '-no-recursion', self.folders_rel[0] ]), self.folders_rel[:2] )

        # test bogus path
        self.assertEqual(self.run_argv([ '-readable', '-vector', 'sh_find', 'bogus' ]), [''] )
