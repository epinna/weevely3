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
BASE_FOLDER="{config.base_folder}/test_file_tar/"
rm -rf "$BASE_FOLDER"

mkdir -p "$BASE_FOLDER/dir1/dir2/dir3/dir4"

echo -n 1 > "$BASE_FOLDER/dir1/f1"
echo -n 1 > "$BASE_FOLDER/dir1/dir2/f2"
echo -n 1 > "$BASE_FOLDER/dir1/dir2/dir3/f3"
echo -n 1 > "$BASE_FOLDER/dir1/dir2/dir3/dir4/f4"

tar cf "$BASE_FOLDER/test_0.tar" -C "$BASE_FOLDER" "dir1/"

echo -n 1 > "$BASE_FOLDER/f5"

rm -rf "$BASE_FOLDER/dir1"

chown www-data: -R "$BASE_FOLDER/"

""".format(
config = config
), shell=True)

class FileTar(BaseTest):

    folders_rel = [
        'test_file_tar/dir1',
        'test_file_tar/dir1/dir2',
        'test_file_tar/dir1/dir2/dir3',
        'test_file_tar/dir1/dir2/dir3/dir4',
    ]
    folders_abs = [ 
        os.path.join(config.base_folder, f) 
        for f in folders_rel 
    ]
    
    files_rel = [
        'test_file_tar/dir1/f1',
        'test_file_tar/dir1/dir2/f2',
        'test_file_tar/dir1/dir2/dir3/f3',
        'test_file_tar/dir1/dir2/dir3/dir4/f4',
    ]
    files_abs = [ 
        os.path.join(config.base_folder, f) 
        for f in files_rel 
    ]
        
    tars_rel = [
        'test_file_tar/test_0.tar'
    ]
    tars_abs = [ 
        os.path.join(config.base_folder, f) 
        for f in tars_rel 
    ]
    
    other_file_rel = 'test_file_tar/f5'
    other_file_abs = os.path.join(config.base_folder, other_file_rel) 
    
    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.run_argv = modules.loaded['file_tar'].run_argv

    def test_compress_decompress(self):

        # Uncompress test.tar
        self.assertTrue(self.run_argv(["--decompress", self.tars_rel[0], 'test_file_tar/' ]));
        for file in self.files_abs:
            self.assertEqual(subprocess.check_output("cat %s" % file, shell=True), b'1')
        for folder in self.folders_abs:
            subprocess.check_call('stat -c %%a "%s"' % folder, shell=True)

        # Compress it again giving starting folder
        self.assertTrue(self.run_argv(['test_file_tar/test_1.tar', self.folders_rel[0]]));
        self.tars_rel.append('test_file_tar/test_1.tar')
        self.tars_abs.append(os.path.join(config.base_folder, self.tars_rel[-1]))

        # Uncompress the new archive and recheck
        self.assertTrue(self.run_argv(["--decompress", 'test_file_tar/test_1.tar', 'test_file_tar/']));
        for file in self.files_abs:
            self.assertEqual(subprocess.check_output("cat %s" % file, shell=True), b'1')
        for folder in self.folders_abs:
            subprocess.check_call('stat -c %%a "%s"' % folder, shell=True)

    def test_compress_multiple(self):
    
        # Uncompress test.tar
        self.assertTrue(self.run_argv(["--decompress", self.tars_rel[0], 'test_file_tar/' ]));
        for file in self.files_abs:
            self.assertEqual(subprocess.check_output("cat %s" % file, shell=True), b'1')
        for folder in self.folders_abs:
            subprocess.check_call('stat -c %%a "%s"' % folder, shell=True)
    
        # Create a new tar adding also other_file
        self.assertTrue(self.run_argv(['test_file_tar/test_2.tar', self.folders_rel[0], self.other_file_rel]));
        self.tars_rel.append('test_file_tar/test_2.tar')
        self.tars_abs.append(os.path.join(config.base_folder, self.tars_rel[-1]))
    
        # Remove all the files
        subprocess.check_output("rm -rf %s" % self.folders_abs[0], shell=True)
        subprocess.check_output("rm %s" % self.other_file_abs, shell=True)

        # Uncompress the new archive and recheck
        self.assertTrue(self.run_argv(["--decompress", 'test_file_tar/test_2.tar', 'test_file_tar/']));
        for file in self.files_abs:
            self.assertEqual(subprocess.check_output("cat %s" % file, shell=True), b'1')
        for folder in self.folders_abs:
            subprocess.check_call('stat -c %%a "%s"' % folder, shell=True)

        self.assertEqual(subprocess.check_output("cat %s" % self.other_file_abs, shell=True), b'1')

    @log_capture()
    def test_already_exists(self, log_captured):
    
            # Create a new tar with other_file, with the name test_0.tar
        self.assertIsNone(self.run_argv(['test_file_tar/test_0.tar', self.other_file_rel]));
        self.assertEqual(log_captured.records[-1].msg,
                         "File 'test_file_tar/test_0.tar' already exists, skipping compressing")
    

    @log_capture()
    def test_unexistant_decompress(self, log_captured):
    
        self.assertIsNone(self.run_argv(["--decompress", 'bogus', '.']));
        self.assertEqual(log_captured.records[-1].msg,
                         "Skipping file 'bogus', check existance and permission")
    
    
    @log_capture()
    def test_unexistant_compress(self, log_captured):
    
        self.assertIsNone(self.run_argv(['bogus.tar', 'bogus']));
        self.assertEqual(log_captured.records[-1].msg,
                         "File 'bogus.tar' not created, check existance and permission")
    
