from core.channels.channel import Channel
from testsuite.base_test import BaseTest
import utils
from testsuite import config
from core.weexceptions import DevException
import utils
import subprocess
import random
import os

class BaseFilesystem(BaseTest):

    def populate_folders(self, deepness = 4):
        """Generate a folder tree with random names.

        Args:
            deepness (int): How much is deep the folder tree

        Returns:
            A set of two strings, dir_abs_path and dir_rel_path
        """

        folders_abs = [ config.script_folder ]

        for folder in [ utils.strings.randstr() for f in range(0, deepness) ]:

            folders_abs.append(os.path.join(*[ folders_abs[-1], folder ] ))
            self.check_call(
                config.cmd_env_mkdir_s % (folders_abs[-1]),
                shell=True)

        folders_rel = [ f.replace(config.script_folder, '') for f in folders_abs[1:] ]

        return folders_abs[1:], folders_rel

    def populate_files(self, dir_abs_paths, file_name_list = [], file_content_list = []):

        """Populate a folder tree with files with random names.

        Args:
            dir_abs_path (list of str): List of folders to populate

        Returns:
            A set of file_abs_path, file_rel_path
        """

        files_abs = []
        files_rel = []

        if file_content_list and len(file_content_list) != len(file_name_list):
            raise DevException("Error, file names and contents lists have different lengths.")

        for folder_abs in dir_abs_paths:
            file_name = file_name_list.pop(0) if file_name_list else utils.strings.randstr()

            files_abs.append(os.path.join(folder_abs, file_name))
            files_rel.append(files_abs[-1].replace(config.script_folder, ''))
            self.check_call(
                config.cmd_env_content_s_to_s % ('1' if not file_content_list else file_content_list.pop(0), files_abs[-1]),
                shell=True)

        return files_abs, files_rel
