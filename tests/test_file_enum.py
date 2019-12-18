from testfixtures import log_capture
from tests.base_test import BaseTest
from core.sessions import SessionURL
from core import modules
from tests import config
import utils
from core import messages
import subprocess
import tempfile
import os

def setUpModule():
    subprocess.check_output("""
BASE_FOLDER="{config.base_folder}/test_file_enum/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/dir4"

touch "$BASE_FOLDER/dir1/0111-exec"
chmod 0111 "$BASE_FOLDER/dir1/0111-exec"

touch "$BASE_FOLDER/dir1/dir2/0222-write"
chmod 0222 "$BASE_FOLDER/dir1/dir2/0222-write"

touch "$BASE_FOLDER/dir1/dir2/dir3/0000"
chmod 0000 "$BASE_FOLDER/dir1/dir2/dir3/0000"
""".format(
config = config
), shell=True)

class FileEnum(BaseTest):

    files_rel = [
        'test_file_enum/dir1/0111-exec',
        'test_file_enum/dir1/dir2/0222-write',
        'test_file_enum/dir1/dir2/dir3/0000',
    ]

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.run_argv = modules.loaded['file_enum'].run_argv

    def test_file_enum(self):

        # Enum self.files_rel[:2] passed with arguments
        self.assertEqual(self.run_argv( self.files_rel[:3] ), {
                    self.files_rel[0] :  'ex',
                    self.files_rel[1] :  'ew',
                    self.files_rel[2] :  'e' 
        })

        # Enum self.files_rel[:2] + bogus passed with arguments
        self.assertEqual(self.run_argv( self.files_rel[:3] + [ 'bogus' ] ), {
                    self.files_rel[0] :  'ex',
                    self.files_rel[1] :  'ew',
                    self.files_rel[2] :  'e' 
        })

        # Enum self.files_rel[:2] + bogus passed with arguments and -print
        self.assertEqual(self.run_argv( self.files_rel[:3] + [ 'bogus', '-print' ] ), {
                    self.files_rel[0] :  'ex',
                    self.files_rel[1] :  'ew',
                    self.files_rel[2] :  'e',
                    'bogus' : ''
        })

    def test_file_enum_lpath(self):

        # Enum self.files_rel[:2] passed with lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3]).encode('utf-8'))
        temp_file.flush()
        self.assertEqual(self.run_argv( [ '-lpath-list', temp_file.name ] ), {
            self.files_rel[0] :  'ex',
            self.files_rel[1] :  'ew',
            self.files_rel[2] :  'e' 
        })
        temp_file.close()

        # Enum self.files_rel[:2] + bogus passed with lfile
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3] + [ 'bogus' ]).encode('utf-8'))
        temp_file.flush()
        self.assertEqual(self.run_argv( [ '-lpath-list', temp_file.name ] ), {
            self.files_rel[0] : 'ex' ,
            self.files_rel[1] : 'ew' ,
            self.files_rel[2] : 'e' 
        })
        temp_file.close()

        # Enum self.files_rel[:2] + bogus passed with lfile and -print
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write('\n'.join(self.files_rel[:3] + [ 'bogus' ]).encode('utf-8'))
        temp_file.flush()
        self.assertEqual(self.run_argv( [ '-lpath-list', temp_file.name, '-print' ] ), {
                    self.files_rel[0] :  'ex' ,
                    self.files_rel[1] :  'ew' ,
                    self.files_rel[2] :  'e' ,
                    'bogus' : ''
        })
        temp_file.close()

    @log_capture()
    def test_err(self, log_captured):

        self.assertIsNone(self.run_argv( [ '-lpath-list', 'bogus' ] ))
        self.assertEqual(messages.generic.error_loading_file_s_s[:19],
                         log_captured.records[-1].msg[:19])
