from testfixtures import log_capture
from testsuite.base_fs import BaseFilesystem
from testsuite import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os
import tempfile
import random

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
                                [ 'string1', 'string12', 'string3\nSTR33', 'string4' ]
                            )

        # Change mode of the third file to ---x--x--x 0111 execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0111', self.files_abs[3]),
            shell=True)

        self.vector_list = [
            m for m in modules.loaded['file_grep'].vectors.get_names()
        ]

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

    def test_file_grep(self):

        for vect in self.vector_list:

            # grep string1 -> string[0]
            self.assertEqual(
                self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring1' ])[0],
                              {
                                self.files_rel[0] : ['string1'],
                                self.files_rel[1] : ['string12']
                               }
                            )

            # grep string3 -> []
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4' ])[0],{})

            # grep string[2-9] -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring[2-9]' ])[0],{ self.files_rel[2] : ['string3'] })

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*' ])[0],{ self.files_rel[2] : ['string3'] })


    def test_file_grep_invert(self):

        for vect in self.vector_list:

            # grep -v string1 -> string3
            self.assertEqual(
                self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring1', '-v' ])[0],
                              {
                                self.files_rel[2] : ['string3', 'STR33'],
                                # self.files_rel[3] : ['string4'] # String 4 is 0111
                               }
                            )

            # grep -v bogus -> string1,2,3
            self.assertEqual(
                self.run_argv([ '-vector', vect, self.folders_rel[0], 'bogus', '-v' ])[0],
                              {
                                self.files_rel[0] : ['string1'],
                                self.files_rel[1] : ['string12'],
                                self.files_rel[2] : ['string3', 'STR33']
                               }
                            )

            # grep -v -i STR from string[2] -> string3
            self.assertEqual(self.run_argv([ '-vector', vect, self.files_rel[2], '-v', '-case', 'STR' ])[0],{ self.files_rel[2] : ['string3'] })


    def test_file_grep_output_remote(self):

        for vect in self.vector_list:

            output_path = os.path.join(config.script_folder, 'test_%s_%i' % (vect, random.randint(1,99999)))

            # grep string3 -> []
            self.assertTrue(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4', '-output', output_path ])[1])
            self.assertEqual(self.check_output(
                config.cmd_env_cat_s % (output_path),
                shell=True), ''
            )
            self.check_call(
                config.cmd_env_remove_s % (output_path),
                shell=True)

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*', '-output', output_path ])[0],{ self.files_rel[2] : ['string3'] })
            self.assertEqual(self.check_output(
                config.cmd_env_cat_s % (output_path),
                shell=True), 'string3'
            )
            self.check_call(
                config.cmd_env_remove_s % (output_path),
                shell=True)

    def test_file_grep_output_local(self):


        for vect in self.vector_list:

            temp_file = tempfile.NamedTemporaryFile()

            # grep string3 -> []
            self.assertTrue(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4', '-output', temp_file.name, '-local' ])[1])
            self.assertEqual('', open(temp_file.name,'r').read())
            temp_file.truncate()

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*', '-output', temp_file.name, '-local' ])[0],{ self.files_rel[2] : ['string3'] })
            self.assertEqual('string3', open(temp_file.name,'r').read())
            temp_file.close()


    @log_capture()
    def test_php_err(self, log_captured):

        # wrong rpath generate None and warning print
        self.assertEqual(self.run_argv([ 'bogus', 'tring4' ])[0], None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                         log_captured.records[-1].msg)

        # wrong regex generate None and warning print
        self.assertEqual(self.run_argv([ '\'', 'tring4' ])[0], None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                 log_captured.records[-1].msg)

    @log_capture()
    def test_sh_err(self, log_captured):

        # wrong rpath generate None and warning print
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', 'bogus', 'tring4' ])[0], None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                         log_captured.records[-1].msg)

        # wrong regex generate None and warning print
        self.assertEqual(self.run_argv([ '-vector', 'grep_sh', '\'', 'tring4' ])[0], None)
        self.assertEqual(messages.module_file_grep.failed_retrieve_info,
                 log_captured.records[-1].msg)
