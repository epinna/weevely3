from testfixtures import log_capture
from tests.base_test import BaseTest
from tests import config
from core.sessions import SessionURL
from core import modules
import utils
from core import messages
import subprocess
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_find/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/dir1/0777/dir3/dir4"
chmod 0777 "$BASE_FOLDER/dir1/0777/"

touch "$BASE_FOLDER/dir1/0111-exec"
chmod 0111 "$BASE_FOLDER/dir1/0111-exec"

touch "$BASE_FOLDER/dir1/0777/0222-write"
chmod 0222 "$BASE_FOLDER/dir1/0777/0222-write"

touch "$BASE_FOLDER/dir1/0777/dir3/0333-write-exec"
chmod 0333 "$BASE_FOLDER/dir1/0777/dir3/0333-write-exec"

touch "$BASE_FOLDER/dir1/0777/dir3/dir4/0444-read"
chmod 0444 "$BASE_FOLDER/dir1/0777/dir3/dir4/0444-read"
""".format(
config = config
), shell=True)

class FindPerms(BaseTest):
    
    folders_rel = [
        'test_file_find/dir1',
        'test_file_find/dir1/0777',
        'test_file_find/dir1/0777/dir3',
        'test_file_find/dir1/0777/dir3/dir4',
    ]
    
    files_rel = [
        'test_file_find/dir1/0111-exec',
        'test_file_find/dir1/0777/0222-write',
        'test_file_find/dir1/0777/dir3/0333-write-exec',
        'test_file_find/dir1/0777/dir3/dir4/0444-read',
    ]

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.run_argv = modules.loaded['file_find'].run_argv

    def test_file_find_php(self):

        # find first writable starting from folder[0]
        self.assertEqual(self.run_argv([ '-writable', '-quit', self.folders_rel[0] ]), [ self.folders_rel[1] ])

        # find first writable file from folder[0]
        self.assertEqual(self.run_argv([ '-writable', '-quit', self.folders_rel[0], '-ftype', 'f' ]), [ self.files_rel[1] ])

        # find all executable starting from folder[0]
        self.assertEqual(sorted(self.run_argv([ '-executable', self.folders_rel[0] ])), sorted(self.folders_rel + [  self.files_rel[2], self.files_rel[0] ] ))

        # find all executable starting from folder[0] that matches the regexp 'te-ex' -> folder[2]
        self.assertEqual(self.run_argv([ '-executable', self.folders_rel[0], 'te-ex' ]), [ self.files_rel[2] ])

        # find all starting from folder[0] that matches the regexp 'TE-EX' -> folder[2]
        self.assertEqual(self.run_argv([ self.folders_rel[0], 'TE-EX' ]), [ self.files_rel[2] ])

        # find all  starting from folder[0] that matches the regexp 'TE-EX' and case sensitive -> []
        self.assertEqual(self.run_argv([ '-case', self.folders_rel[0], 'TE-EX' ]), [ '' ])

        # find all readable starting from folder[0]
        self.assertEqual(sorted(self.run_argv([ '-readable', self.folders_rel[0] ])), sorted(self.folders_rel + [  self.files_rel[3] ] ))

        # find all readable starting from folder[0] with a wrong regex -> none
        self.assertEqual(self.run_argv([ '-readable', self.folders_rel[0], 'bogus' ]), [ '' ] )

        # find readable starting from folder[0] with no recursion
        self.assertEqual(sorted(self.run_argv([ '-readable', '-no-recursion', self.folders_rel[0] ])), sorted(self.folders_rel[:2] ))

        # test bogus path
        self.assertEqual(self.run_argv([ '-readable', 'bogus' ]), [''] )


    def test_file_find_sh(self):

        # find first writable starting from folder[0]
        self.assertEqual(self.run_argv([ '-writable', '-vector', 'sh_find', '-quit', self.folders_rel[0] ]), [ self.folders_rel[1] ])

        # find all executable starting from folder[0]
        self.assertEqual(sorted(self.run_argv([ '-executable', '-vector', 'sh_find', self.folders_rel[0] ])), sorted(self.folders_rel + [  self.files_rel[2], self.files_rel[0] ] ))

        # find all executable starting from folder[0] that matches the regexp '-' -> folder[2]
        self.assertEqual(self.run_argv([ '-executable', '-vector', 'sh_find', self.folders_rel[0], 'te-ex' ]), [ self.files_rel[2] ])

        # find all starting from folder[0] that matches the regexp 'TE-EX' -> folder[2]
        self.assertEqual(self.run_argv([ '-vector', 'sh_find', self.folders_rel[0], 'TE-EX' ]), [ self.files_rel[2] ])

        # find all  starting from folder[0] that matches the regexp 'TE-EX' and case sensitive -> []
        self.assertEqual(self.run_argv([ '-case', '-vector', 'sh_find', self.folders_rel[0], 'TE-EX' ]), [ '' ])

        # find all readable starting from folder[0]
        self.assertEqual(sorted(self.run_argv([ '-readable', '-vector', 'sh_find', self.folders_rel[0] ])), sorted(self.folders_rel + [  self.files_rel[3] ] ))

        # find all readable starting from folder[0] with a wrong regex -> none
        self.assertEqual(self.run_argv([ '-readable', self.folders_rel[0], 'bogus' ]), [ '' ] )

        # find readable starting from folder[0] with no recursion
        self.assertEqual(sorted(self.run_argv([ '-readable', '-vector', 'sh_find', '-no-recursion', self.folders_rel[0] ])), sorted(self.folders_rel[:2] ))

        # test bogus path
        self.assertEqual(self.run_argv([ '-readable', '-vector', 'sh_find', 'bogus' ]), [ '' ] )
