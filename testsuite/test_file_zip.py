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

class FileZip(BaseFilesystem):

    def setUp(self):
        self.session = SessionURL(
                    self.url,
                    self.password,
                    volatile = True
                    )

        modules.load_modules(self.session)

        self.folders_abs = []
        self.folders_rel = []
        self.files_abs = []
        self.files_rel = []
        self.zips_abs = []
        self.zips_rel = []

        for index in range(0,1):

            # Create the folder tree
            folders_abs, folders_rel =  self.populate_folders()
            files_abs, files_rel = self.populate_files(
                                folders_abs,
                                [
                                    'f1_%i' % index,
                                    'f2_%i' % index,
                                    'f3_%i' % index,
                                    'f4_%i' % index ]
                            )

            self.folders_abs += folders_abs
            self.folders_rel += folders_rel
            self.files_abs += files_abs
            self.files_rel += files_rel

            self.zips_rel.append('test_%i.zip' % index)
            self.zips_abs.append(os.path.join(config.script_folder, self.zips_rel[index]))

            self.check_call(config.cmd_env_cd_s_zip_s_s % (
                config.script_folder,
                self.zips_rel[index],
                self.folders_rel[index]
                )
            )

            # Now remove the folder tree leaving the zip
            self._delete_tree()

        self.run_argv = modules.loaded['file_zip'].run_argv

    def _delete_tree(self):

        for file in self.files_abs:

            # Drrty fix due to the mod of the files are rwxr--r-- and can't
            # Be changed if also the folder has -x------. Changing both.
            modules.loaded['shell_php'].run_argv(['chmod(dirname("%s"), 0777);' % file])
            modules.loaded['shell_php'].run_argv(['chmod("%s", 0777);' % file])

            self.check_call(config.cmd_env_remove_s % (file))

        for folder in reversed(self.folders_abs):
            self.check_call(config.cmd_env_rmdir_s % (folder))

    def _delete_zips(self):
        for folder in self.zips_abs:
            self.check_call(config.cmd_env_remove_s % (folder))

    def tearDown(self):
        self._delete_tree()
        self._delete_zips()


    def test_compress_decompress(self):

        # Uncompress test.zip
        self.assertTrue(self.run_argv(["--decompress", 'test_0.zip', '.']));
        for file in self.files_abs:
            self.assertEqual(self.check_output(config.cmd_env_print_repr_s % file),'1')
        for folder in self.folders_abs:
            self.check_call(config.cmd_env_stat_permissions_s % folder)

        # Compress it again giving starting folder
        self.assertTrue(self.run_argv(['test_0_1.zip', self.folders_abs[0]]));
        self.zips_rel.append('test_0_1.zip')
        self.zips_abs.append(os.path.join(config.script_folder, self.zips_rel[-1]))

        # Uncompress the new archive and recheck
        self.assertTrue(self.run_argv(["--decompress", 'test_0_1.zip', '.']));
        for file in self.files_abs:
            self.assertEqual(self.check_output(config.cmd_env_print_repr_s % file),'1')
        for folder in self.folders_abs:
            self.check_call(config.cmd_env_stat_permissions_s % folder)
