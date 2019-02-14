from core.vectors import PhpFile
from core.module import Module
from core import modules
from core import messages
from core.loggers import log
import os

class Sql(Module):

    """Bruteforce SQL database."""

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
            PhpFile(
              payload_path = os.path.join(self.folder, 'mysql.tpl'),
              name = 'mysql',
            ),
            PhpFile(
              payload_path = os.path.join(self.folder, 'pgsql.tpl'),
              name = 'pgsql',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'service', 'help' : 'Service to bruteforce', 'choices' : self.vectors.get_names() },
          { 'name' : '-hostname', 'help' : 'Hostname', 'default' : 'localhost' },
          { 'name' : '-users', 'help' : 'Users', 'nargs' : '*', 'default': [] },
          { 'name' : '-pwds', 'help' : 'Passwords', 'nargs' : '*', 'default': [] },
          { 'name' : '-fusers', 'help' : 'Local file path containing users list' },
          { 'name' : '-fpwds', 'help' : 'Local file path containing password list' }
        ])

    def run(self):

        self.args['users'] = self.args.get('users', [])
        if self.args.get('fusers'):
            try:
                self.args['users'] += open(self.args['fusers'], 'r').read().split(os.linesep)
            except Exception as e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (self.args['fusers'], str(e)))
                return

        self.args['pwds'] = self.args.get('pwds', [])
        if self.args.get('fpwds'):
            try:
                self.args['pwds'] += open(self.args['fpwds'], 'r').read().split(os.linesep)
            except Exception as e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (self.args['fpwds'], str(e)))
                return

        if not self.args['users'] or not self.args['pwds']:
            log.error('Error, no users or passwords loaded')
            return

        return self.vectors.get_result(
                name = self.args['service'],
                format_args = self.args
        )
