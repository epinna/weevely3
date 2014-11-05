from testsuite.base_fs import BaseFilesystem
from testfixtures import log_capture
from testsuite import config
from core.sessions import SessionURL
from core import modules
from core import messages
import subprocess
import datetime
import logging
import os

class FileCheck(BaseFilesystem):

    def setUp(self):
        session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(session)

        # Create the folder tree
        self.folders_abs, self.folders_rel =  self.populate_folders()
        self.files_abs, self.files_rel = self.populate_files(
                                self.folders_abs,
                                [ 'executable', 'writable', 'write-executable', 'readable' ]
                            )

        # Change mode of the first file to 777
        self.check_call(
            config.cmd_env_chmod_s_s % ('0777', self.files_abs[0]),
            shell=True)

        # Get the epoch timestamp of file[0]
        self.files_times = [
            int(subprocess.check_output(
                config.cmd_env_stat_time_modif_epoch_s % (self.files_abs[0]),
                shell=True))
        ]

        # Change mode of the forth file to -r--r--r-- 0444 read
        self.check_call(
            config.cmd_env_chmod_s_s % ('0444', self.files_abs[3]),
            shell=True)

        # Change mode of the forth folder to --wx-wx-wx 0333 write & execute
        self.check_call(
            config.cmd_env_chmod_s_s % ('0333', self.folders_abs[3]),
            shell=True)

        self.run_argv = modules.loaded['file_check'].run_argv

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

    def test_check(self):

        # Some check on a file just readable
        self.assertTrue(self.run_argv([ self.files_rel[3], 'exists']))
        self.assertTrue(self.run_argv([ self.files_rel[3], 'readable']))
        self.assertTrue(self.run_argv([ self.files_rel[3], 'file']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'executable']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'writable']))
        self.assertFalse(self.run_argv([ self.files_rel[3], 'dir']))

        # Some check on an unexistant file
        self.assertFalse(self.run_argv(['BOGUS', 'exists']))
        self.assertFalse(self.run_argv(['BOGUS', 'readable']))
        self.assertFalse(self.run_argv(['BOGUS', 'file']))
        self.assertFalse(self.run_argv(['BOGUS', 'executable']))
        self.assertFalse(self.run_argv(['BOGUS', 'writable']))
        self.assertFalse(self.run_argv(['BOGUS', 'dir']))

        # Some check on a folder with jsut x & w
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'exists']))
        self.assertFalse(self.run_argv([ self.folders_rel[3], 'readable']))
        self.assertFalse(self.run_argv([ self.folders_rel[3], 'file']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'executable']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'writable']))
        self.assertTrue(self.run_argv([ self.folders_rel[3], 'dir']))

        # Save the human readable remote file[0] timestamp
        rdatetime = datetime.datetime.fromtimestamp(float(self.files_times[0])).strftime('%Y-%m-%d')

        self.assertTrue(self.run_argv([ self.files_rel[0], 'exists']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'readable']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'file']))
        self.assertFalse(self.run_argv([ self.files_rel[0], 'dir']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'executable']))
        self.assertTrue(self.run_argv([ self.files_rel[0], 'writable']))
        self.assertEqual(self.run_argv([ self.files_rel[0], 'size']), 1)
        self.assertEqual(self.run_argv([ self.files_rel[0], 'md5']), 'c4ca4238a0b923820dcc509a6f75849b')
        self.assertAlmostEqual(self.run_argv([ self.files_rel[0], 'time']), self.files_times[0], delta = 20)
        self.assertEqual(self.run_argv([ self.files_rel[0], 'datetime']).split(' ')[0], rdatetime)
