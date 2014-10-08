from core.vectors import PhpCmd, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random


class Ls(Module):

    """List directory content."""

    aliases = [ 'ls', 'dir' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors([
            ShellCmd(
                payload = "ls ${dir}",
                name = 'ls_sh',
                arguments = [
                  "-stderr_redirection",
                  " 2>/dev/null",
                ]
            ),
            PhpCmd(
                payload = """
                $p="${dir}";
                if(@is_dir($p)){
                    $d=@opendir($p);
                    $a=array();
                    if($d){
                        while(($f=@readdir($d))) $a[]=$f;
                        sort($a);
                        print(join(PHP_EOL,$a));
                    }
                }""",
                name = 'ls_php'
            )
        ])

        self.register_arguments([
          { 'name' : 'dir', 'help' : 'Target folder', 'default' : '.', 'nargs' : '?' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names() }
        ])

    def run(self, args):

        vname, result = self.vectors.find_first_result(
            names = [ args.get('vector') ],
            format_args = args,
            # This check is redundant but is needed
            # to loop all vectors. This helps to skip the
            # disabled vectors.
            condition = lambda r: r
        )

        return result.split('\n') if result else None

    def print_result(self, result):
        if result: log.info('\n'.join(result))
