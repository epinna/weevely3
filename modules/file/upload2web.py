from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import urlparse
import os

class Upload2web(Module):

    """Upload file automatically to a web folder and get corresponding URL"""

    aliases = [ 'rm' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            { 'name' : 'lpath', 'help' : 'Local file path', 'nargs' : '?' },
            { 'name' : 'rpath', 'help' : 'Path. If is a folder find the first writable folder in it.', 'default' : '.', 'nargs' : '?' },
        ])

    def _get_env_info(self, script_url):

        script_folder_data = ModuleExec('system_info', [ '-info', 'script_folder' ]).run()
        if not script_folder_data or not script_folder_data.get('script_folder'): return

        script_folder = script_folder_data.get('script_folder')
        script_url_splitted = urlparse.urlsplit(script_url)
        script_url_path_folder, script_url_path_filename = os.path.split(
            script_url_splitted.path)

        url_folder_pieces = script_url_path_folder.split(os.sep)
        folder_pieces = script_folder.split(os.sep)

        for pieceurl, piecefolder in zip(reversed(url_folder_pieces), reversed(folder_pieces)):
            if pieceurl == piecefolder:
                folder_pieces.pop()
                url_folder_pieces.pop()
            else:
                break

        base_url_path_folder = os.sep.join(url_folder_pieces)
        self.base_folder_url = urlparse.urlunsplit(
            script_url_splitted[:2] + (base_url_path_folder, ) + script_url_splitted[3:])
        self.base_folder_path = os.sep.join(folder_pieces)

    def _map_folder2web(self, relative_path_folder='.'):

        absolute_path = ModuleExec('file_check', [ '.', 'abspath' ]).run()

        if not absolute_path:
            log.warn(messages.module_file_upload2web.failed_resolve_path)
            return None, None

        if not absolute_path.startswith(self.base_folder_path.rstrip('/')):
            log.warn(messages.module_file_upload2web.error_s_not_under_webroot_s % (
                        absolute_path,
                        self.base_folder_path.rstrip('/'))
            )
            return None, None

        relative_to_webroot_path = absolute_path.replace(
                                        self.base_folder_path,
                                        ''
                                    )

        url_folder = '%s/%s' % (self.base_folder_url.rstrip('/'),
                                relative_to_webroot_path.lstrip('/'))

        return absolute_path, url_folder

    def _map_file2web(self, relative_path_file):

        relative_path_folder, filename = os.path.split(relative_path_file)
        if not relative_path_folder:
            relative_path_folder = './'

        absolute_path_folder, url_folder = self._map_folder2web(
            relative_path_folder)

        if not absolute_path_folder or not url_folder:
            return None, None

        absolute_path_file = os.path.join(absolute_path_folder, filename)
        url_file = os.path.join(url_folder, filename)

        return absolute_path_file, url_file

    def run(self, args):

        self._get_env_info(self.session['url'])
        if not self.base_folder_url or not self.base_folder_path:
            log.warn(messages.module_file_upload2web.failed_retrieve_info)

        # If remote path is a folder, get first readable folder
        # TODO: add type check in file_find
