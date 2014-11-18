from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import tempfile
import os

class FileEnum(BaseFilesystem):

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

        # Change mode of the third file to 0000
        self.check_call(
            config.cmd_env_chmod_s_s % ('0000', self.files_abs[2]),
            shell=True)

        self.run_argv = modules.loaded['file_enum'].run_argv

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

    def test_file_enum(self):

        # Enum self.files_rel[:2] passed with arguments
        self.assertItemsEqual(self.run_argv( self.files_rel[:3] ), {
                    self.files_rel[0] : [ 'ex' ],
                    self.files_rel[1] : [ 'ew' ],
                    self.files_rel[2] : [ 'e' ]
        })

        # Enum self.files_rel[:2] + bogus passed with arguments
        self.assertItemsEqual(self.run_argv( self.files_rel[:3] + [ 'bogus' ] ), {
                    self.files_rel[0] : [ 'ex' ],
                    self.files_rel[1] : [ 'ew' ],
                    self.files_rel[2] : [ 'e' ]
        })

        # Enum self.files_rel[:2] + bogus passed with arguments and -print
        self.assertItemsEqual(self.run_argv( self.files_rel[:3] + [ 'bogus', '-print' ] ), {
                    self.files_rel[0] : [ 'ex' ],
                    self.files_rel[1] : [ 'ew' ],
                    self.files_rel[2] : [ 'e' ],
                    'bogus' : []
        })

    def test_file_enum_lpath(self):

        # Enum self.files_rel[:2] passed with lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3]))
        temp_file.flush()
        self.assertItemsEqual(self.run_argv( [ '-lpath-list', temp_file.name ] ), {
            self.files_rel[0] : [ 'ex' ],
            self.files_rel[1] : [ 'ew' ],
            self.files_rel[2] : [ 'e' ]
        })
        temp_file.close()

        # Enum self.files_rel[:2] + bogus passed with lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3] + [ 'bogus' ]))
        temp_file.flush()
        self.assertItemsEqual(self.run_argv( [ '-lpath-list', temp_file.name ] ), {
            self.files_rel[0] : [ 'ex' ],
            self.files_rel[1] : [ 'ew' ],
            self.files_rel[2] : [ 'e' ]
        })
        temp_file.close()

        # Enum self.files_rel[:2] + bogus passed with lfile and -print
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3] + [ 'bogus' ]))
        temp_file.flush()
        self.assertItemsEqual(self.run_argv( [ '-lpath-list', temp_file.name, '-print' ] ), {
                    self.files_rel[0] : [ 'ex' ],
                    self.files_rel[1] : [ 'ew' ],
                    self.files_rel[2] : [ 'e' ],
                    'bogus' : []
        })
        temp_file.close()

    @log_capture()
    def test_err(self, log_captured):

        self.assertIsNone(self.run_argv( [ '-lpath-list', 'bogus' ] ))
        self.assertEqual(messages.generic.error_loading_file_s_s[:19],
                         log_captured.records[-1].msg[:19])
