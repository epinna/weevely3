from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core.loggers import log
from core import messages
from core import modules

class Grep(Module):

    """Print lines matching a pattern in multiple files."""

    aliases = [ 'grep' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        # The grep action is done using multiple request.
        # First search for writable file, and then execute the grep
        # code for every found file. This allows to reuse code in
        # find_perm module and reduce the chances of timeout.

        self.register_vectors(
            [
            ShellCmd(
                payload = "grep ${ '' if case else '-i' } -e '${regex}' '${rfile}'",
                name = "grep_sh",
                arguments = [
                  "-stderr_redirection",
                  " 2>/dev/null",
                ]
            ),
            PhpCode(
                payload = """$m=Array();preg_match_all("/.*${regex}.*/${ '' if case else 'i'}",file_get_contents('${rfile}'),$m);if($m) print(implode(PHP_EOL,$m[0]));""",
                name = "grep_php"
            )
            ]
        )

        self.register_arguments([
            { 'name' : 'rpath', 'help' : 'Path. If is a folder grep all the contained files.' },
            { 'name' : 'regex', 'help' : 'Regular expression to match file name' },
            { 'name' : '-case', 'help' : 'Search case sensitive expression', 'action' : 'store_true', 'default' : False },
            { 'name' : '-name-regex', 'help' : 'Regular expression to match file name to grep' },
            { 'name' : '-no-recursion', 'action' : 'store_true', 'default' : False },
            { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'grep_php' },
        ])

    def run(self, args):


        files = []

        if ModuleExec("file_check", [ args['rpath'], 'dir' ]).run():
            # If remote path is a folder, harvest all the readable
            # files wih given name-regex

            # Prepare the arguments for find_perms
            find_perms_args = [ '-readable', args['rpath'] ]
            if args.get('name_regex'):
                find_perms_args += [ '-name-regex', args.get('name_regex') ]
            if args.get('no_recursion'):
                find_perms_args += [ '-no-recursion' ]

            files = ModuleExec("find_perms", find_perms_args).run()


        elif (ModuleExec("file_check", [ args['rpath'], 'file' ]).run() and
              ModuleExec("file_check", [ args['rpath'], 'readable' ]).run()):
            # If the remote path is a readable file, just store the path
            files = [ args['rpath'] ]


        # Validate files presence
        if not isinstance(files, list) or not files:
            log.warn(messages.module_file_grep.failed_retrieve_info)
            return

        # Store the found data in data dictionary in the
        # form `{ filename : [ line1, line2, ... ] }`
        results = {}

        for rfile in files:
            result = self.vectors.get_result(
                args['vector'],
                { 'regex' : args['regex'], 'rfile' : rfile, 'case' : args['case'] }
            )

            result_list = result.split('\n') if isinstance(result, str) and result else []

            if result_list:

                if len(files) > 1:
                    # Print filepath:line if there are multiple files

                    for line in result_list:
                        log.info('%s:%s' % ( rfile, line ))
                else:
                    # Else, just print the lines
                    log.info('\n'.join(result_list))

                results[rfile] = result_list

        return results

    def print_result(self, result):
        pass
