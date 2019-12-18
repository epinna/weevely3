from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import urllib.parse
import os

class Upload2web(Module):

    """Upload file automatically to a web folder and get corresponding URL."""

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
            { 'name' : 'lpath', 'help' : 'Local file path. Set remote file name when used with -content.' },
            { 'name' : 'rpath', 'help' : 'Remote path. If it is a folder find the first writable folder in it', 'default' : '.', 'nargs' : '?' },
            { 'name' : '-content', 'help' : 'Optionally specify the file content'},
            { 'name' : '-simulate', 'help' : 'Just return the positions without uploading any content', 'action' : 'store_true', 'default' : False },
        ])

    def _get_env_info(self, script_url):

        script_folder = ModuleExec('system_info', [ '-info', 'script_folder' ]).load_result_or_run('script_folder')
        if not script_folder: return

        script_url_splitted = urllib.parse.urlsplit(script_url)
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
        self.base_folder_url = urllib.parse.urlunsplit(
            script_url_splitted[:2] + (base_url_path_folder, ) + script_url_splitted[3:])
        self.base_folder_path = os.sep.join(folder_pieces)

    def _map_folder2web(self, relative_path_folder='.'):

        absolute_path = ModuleExec('file_check', [ relative_path_folder, 'abspath' ]).run()

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

    def run(self):

        file_upload_args = [ self.args['rpath'] ]

        content = self.args.get('content')
        lpath = self.args.get('lpath')
            
        self._get_env_info(self.session['url'])
        if not self.base_folder_url or not self.base_folder_path:
            log.warn(messages.module_file_upload2web.failed_retrieve_info)

        # If remote path is a folder, get first writable folder
        if ModuleExec("file_check", [ self.args['rpath'], 'dir' ]).run():
            folders = ModuleExec("file_find", [ '-writable', '-quit', self.args['rpath'] ]).run()

            if not folders or not folders[0]:
                log.warn(messages.module_file_upload2web.failed_search_writable_starting_s % self.args['rpath'])
                return None, None

            # Get remote file name from lpath
            lfolder, rname = os.path.split(lpath)

            # TODO: all the paths should be joined with remote OS_SEP from system_info.
            self.args['rpath'] = os.path.join(folders[0], rname)

        file_upload_args = [ lpath, self.args['rpath'] ]
        if content:
            file_upload_args += [ '-content', content ]
            
        if self.args.get('simulate') or ModuleExec("file_upload", file_upload_args).run():
            # Guess URL from rpath
            return [ self._map_file2web(self.args['rpath']) ]
