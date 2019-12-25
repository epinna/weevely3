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
                payload = "grep ${ '' if case else '-i' } ${ '-v' if invert else '' } -e '${regex}' '${rfile}'",
                name = "grep_sh",
                arguments = [
                  "-stderr_redirection",
                  " 2>/dev/null",
                ]
            ),
            PhpCode(
                payload = """% if invert:
$m=file_get_contents("${rfile}");$a=preg_replace("/${'' if regex.startswith('^') else '.*' }${regex.replace('/','\/')}${'' if regex.endswith('$') else '.*' }".PHP_EOL."?/m${ '' if case else 'i'}","",$m);if($a)print($a);
% else:
$m=Array();preg_match_all("/${'' if regex.startswith('^') else '.*' }${regex.replace('/','\/')}${'' if regex.endswith('$') else '.*' }/m${ '' if case else 'i'}",file_get_contents('${rfile}'),$m);if($m) print(implode(PHP_EOL,$m[0]));
% endif""",
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
            { 'name' : '-output', 'help' : 'Redirect output to remote file' },
            { 'name' : '-v', 'dest' : 'invert', 'action' : 'store_true', 'default' : False, 'help' : 'Invert matching to select non-matching lines' },
            { 'name' : '-local', 'action' : 'store_true', 'default' : False, 'help' : 'Save redirected output locally' },
            { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : 'grep_php' },
        ])

    def run(self):

        files = []

        if ModuleExec("file_check", [ self.args['rpath'], 'dir' ]).run():
            # If remote path is a folder, harvest all the readable
            # files wih given name-regex

            # Prepare the arguments for file_find
            file_find_args = [ '-readable', self.args['rpath'], '-ftype', 'f' ]
            if self.args.get('name_regex'):
                file_find_args += [ '-name-regex', self.args.get('name_regex') ]
            if self.args.get('no_recursion'):
                file_find_args += [ '-no-recursion' ]

            files = ModuleExec("file_find", file_find_args).run()


        elif (ModuleExec("file_check", [ self.args['rpath'], 'file' ]).run() and
              ModuleExec("file_check", [ self.args['rpath'], 'readable' ]).run()):
            # If the remote path is a readable file, just store the path
            files = [ self.args['rpath'] ]

        # Validate files presence
        if not isinstance(files, list) or not files:
            log.warning(messages.module_file_grep.failed_retrieve_info)
            return None, False

        # Store the found data in data dictionary in the
        # form `{ filename : [ line1, line2, ... ] }`
        # and store them as string whether requested
        results = {}
        output_str = ''
        output_path = self.args.get('output')

        for rfile in files:
            result_str = self.vectors.get_result(
                self.args['vector'],
                { 'regex' : self.args['regex'], 'rfile' : rfile, 'case' : self.args['case'], 'invert' : self.args['invert'] }
            )

            # Both grep_sh and grep_php -v trail a \n, this should work fine
            result_str = result_str[:-1] if result_str and result_str.endswith('\n') else result_str

            result_list = result_str.split('\n') if isinstance(result_str, str) and result_str else []

            # This means the command returned something something
            if result_list:

                if output_path:
                    # If output is redirected, just append to output_str
                    output_str += result_str

                else:
                    # Else, print it out
                    if len(files) > 1:
                        # Print filepath:line if there are multiple files

                        for line in result_list:
                            log.info('%s:%s' % ( rfile, line ))
                    else:
                        # Else, just print the lines
                        log.info('\n'.join(result_list))

                results[rfile] = result_list

        # Save output to file whether specified
        saved = False
        if output_path:
            if not self.args.get('local'):
                saved = ModuleExec('file_upload', [ '-content', result_str, output_path ]).run()
            else:
                try:
                    with open(output_path, 'wb') as outputfile:
                        outputfile.write(result_str.encode('utf-8'))
                except Exception as e:
                    log.warning(
                      messages.generic.error_loading_file_s_s % (output_path, str(e)))
                else:
                    saved = True

        return results, saved

    def print_result(self, result):
        pass
