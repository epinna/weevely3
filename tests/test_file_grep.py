from testfixtures import log_capture
from tests.base_test import BaseTest
from tests import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os
import tempfile
import random

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_grep/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/dir4"

echo string1 > "$BASE_FOLDER/dir1/string1"
echo string12 > "$BASE_FOLDER/dir1/dir2/string12"
echo 'string3\nSTR33' > "$BASE_FOLDER/dir1/dir2/dir3/string3"
echo string4 > "$BASE_FOLDER/dir1/dir2/dir3/dir4/string4"
chmod 0111 "$BASE_FOLDER/dir1/dir2/dir3/dir4/string4"
chown www-data: -R "$BASE_FOLDER/"

""".format(
config = config
), shell=True)

class FileGrep(BaseTest):

    folders_rel = [
        'test_file_grep/dir1',
        'test_file_grep/dir1/dir2',
        'test_file_grep/dir1/dir2/dir3',
        'test_file_grep/dir1/dir2/dir3/dir4',
    ]
    
    files_rel = [
        'test_file_grep/dir1/string1',
        'test_file_grep/dir1/dir2/string12',
        'test_file_grep/dir1/dir2/dir3/string3',
        'test_file_grep/dir1/dir2/dir3/dir4/string4',
    ]

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.vector_list = modules.loaded['file_grep'].vectors.get_names()

        self.run_argv = modules.loaded['file_grep'].run_argv

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
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4' ])[0], {})

            # grep string[2-9] -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring[2-9]' ])[0], { self.files_rel[2] : ['string3'] })

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*' ])[0], { self.files_rel[2] : ['string3'] })


    def test_file_grep_invert(self):

        for vect in self.vector_list:

            # grep -v string1 -> string3
            self.assertEqual(
                self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring1', '-v' ])[0],
                              {
                                self.files_rel[2]: ['string3', 'STR33'],
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
            self.assertEqual(self.run_argv([ '-vector', vect, self.files_rel[2], '-v', '-case', 'STR' ])[0], { self.files_rel[2] : ['string3'] })


    def test_file_grep_output_remote(self):

        for vect in self.vector_list:

            output_path = os.path.join(config.base_folder, 'test_file_grep', 'test_%s_%i' % (vect, random.randint(1, 99999)))

            # grep string3 -> []
            self.assertTrue(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4', '-output', output_path ])[1])
            self.assertEqual(subprocess.check_output(
                    'cat "%s"' % (output_path),
                    shell=True
                ), b''
            )
            
            subprocess.check_output(
                'rm -f %s' % (output_path),
                shell=True)

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*', '-output', output_path ])[0], { self.files_rel[2] : ['string3'] })
            self.assertEqual(subprocess.check_output(
                'cat "%s"' % (output_path),
                shell=True), b'string3'
            )
            subprocess.check_output(
                'rm -f %s' % (output_path),
                shell=True)

    def test_file_grep_output_local(self):

        for vect in self.vector_list:

            temp_file = tempfile.NamedTemporaryFile()

            # grep string3 -> []
            self.assertTrue(self.run_argv([ '-vector', vect, self.folders_rel[0], 'tring4', '-output', temp_file.name, '-local' ])[1])
            with open(temp_file.name, 'r') as temp_file2:
                self.assertEqual('', temp_file2.read())
            temp_file.truncate()

            # grep rpath=folder2 string -> string[3]
            self.assertEqual(self.run_argv([ '-vector', vect, self.folders_rel[2], 'string.*', '-output', temp_file.name, '-local' ])[0], { self.files_rel[2] : ['string3'] })
            with open(temp_file.name, 'r') as temp_file2:
                self.assertEqual('string3', temp_file2.read())
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
