from core.vectors import PhpCmd, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random


class Ls(Module):

    """List directory content ('ls' replacement)"""

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
            ),
            ShellCmd(
                payload = "ls -a ${dir}",
                name = 'ls_sh',
                arguments = [
                  "-stderr_redirection",
                  " 2>/dev/null",
                ]
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
            # This condition is reduntant but is needed
            # to just loop all vectors. This helps to skip the
            # disabled vectors.
            condition = lambda r: r
        )

        return result.split('\n') if result else None

    def print_result(self, result):
        if result: log.info('\n'.join(result))
