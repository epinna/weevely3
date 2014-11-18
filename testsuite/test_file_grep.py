from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os

class FileGrep(BaseFilesystem):

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
                                [ 'string1', 'string12', 'string3', 'string4' ],
                                [ 'string1', 'string12', 'string3', 'string4' ]
                            )

        # Change mode of the third file to ---x--x--x 0111 execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0111', self.files_abs[3]),
            shell=True)

        self.run_argv = modules.loaded['file_grep'].run_argv

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

    def test_file_grep_php(self):

        # grep string1 -> string[0]
        self.assertEqual(
            self.run_argv([ self.folders_rel[0], 'tring1' ]),
                          {
                            self.files_rel[0] : ['string1'],
                            self.files_rel[1] : ['string12']
                           }
                        )

        # grep string3 -> []
        self.assertEqual(self.run_argv([ self.folders_rel[0], 'tring4' ]),{})

        # grep string[2-9] -> string[3]
        self.assertEqual(self.run_argv([ self.folders_rel[0], 'tring[2-9]' ]),{ self.files_rel[2] : ['string3'] })

        # grep rpath=folder2 string -> string[3]
        self.assertEqual(self.run_argv([ self.folders_rel[2], 'string.*' ]),{ self.files_rel[2] : ['string3'] })


    def test_file_grep_sh(self):

        # grep string1 -> string[0]
        self.assertEqual(
            self.run_argv([ '-vector', 'grep_sh', self.folders_rel[0], 'tring1' ]),
                          {
                            self.files_rel[0] : ['string1'],
                            self.files_rel[1] : ['string12']
                           }
                        )

        # grep string3 -> []
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', self.folders_rel[0], 'tring4' ]),{})

        # grep string[2-9] -> string[3]
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', self.folders_rel[0], 'tring[2-9]' ]),{ self.files_rel[2] : ['string3'] })

        # grep rpath=folder2 string -> string[3]
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', self.folders_rel[2], 'string.*' ]),{ self.files_rel[2] : ['string3'] })


    @log_capture()
    def test_php_err(self, log_captured):

        # wrong rpath generate None and warning print
        self.assertEqual(self.run_argv([ 'bogus', 'tring4' ]), None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                         log_captured.records[-1].msg)

        # wrong regex generate None and warning print
        self.assertEqual(self.run_argv([ '\'', 'tring4' ]), None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                 log_captured.records[-1].msg)

    @log_capture()
    def test_sh_err(self, log_captured):

        # wrong rpath generate None and warning print
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', 'bogus', 'tring4' ]), None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                         log_captured.records[-1].msg)

        # wrong regex generate None and warning print
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', '\'', 'tring4' ]), None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                 log_captured.records[-1].msg)
