from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import modules
from core import messages
import tempfile
import subprocess
import hashlib
import base64
import re

class Edit(Module):

    """Edit remote file on a local editor."""

    aliases = [
        'vi',
        'vim',
        'emacs',
        'nano',
        'pico',
        'gedit',
        'kwrite'
    ]

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
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : '-vector', 'choices' : ( 'file', 'fread', 'file_get_contents', 'base64' ) },
          { 'name' : '-keep-ts', 'action' : 'store_true', 'default' : False },
          { 'name' : '-editor', 'help' : 'Choose editor', 'default' : 'vim' }
        ])

    def run(self):

        # Get a temporary file name
        suffix = re.sub('[\W]+', '_', self.args['rpath'])
        temp_file = tempfile.NamedTemporaryFile(suffix = suffix)
        lpath = temp_file.name

        # Keep track of the old timestamp if requested
        if self.args['keep_ts']:
            timestamp = ModuleExec(
                        'file_check',
                        [ self.args.get('rpath'), 'time' ]
                    ).run()

        # If remote file already exists and readable
        if ModuleExec(
                    'file_check',
                    [ self.args.get('rpath'), 'readable' ]
                ).run():

            # Download file
            result_download = ModuleExec(
                        'file_download',
                        [ self.args.get('rpath'), lpath ]
                    ).run()

            # Exit with no result
            # The error should already been printed by file_download exec
            if result_download == None: return

            # Store original md5
            md5_orig = hashlib.md5(open(lpath, 'rb').read()).hexdigest()

            # Run editor
            subprocess.check_call( [ self.args['editor'], lpath ])

            # With no changes, just return
            if md5_orig == hashlib.md5(open(lpath, 'rb').read()).hexdigest():
                log.debug(messages.module_file_edit.unmodified_file)
                temp_file.close()
                return

        else:
            subprocess.check_call( [ self.args['editor'], lpath ])

        # Upload file
        result_upload = ModuleExec(
                    'file_upload',
                    [ '-force', lpath, self.args.get('rpath') ]
                ).run()


        # Reset original timestamp if requested
        if self.args['keep_ts']:
            ModuleExec(
                'file_touch',
                [ self.args.get('rpath'), '-epoch-ts', str(timestamp) ]
            ).run()

        # Delete temp file
        temp_file.close()

        return result_upload

    def run_alias(self, line, cmd):

        # Run this alias independently from the shell_sh status.
        # Also, set the proper editor to run
        return self.run_cmdline('%s -editor %s' % (line, cmd))
