from core.vectors import PhpCode
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

        self.register_arguments([
          { 'name' : 'dir', 'help' : 'Target folder', 'nargs' : '?', 'default' : '.' }
        ])

    def run(self):

        return PhpCode("""
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
                postprocess = lambda x: x.split('\n') if x else []
               ).run(self.args)

    def print_result(self, result):
        if result: log.info('\n'.join(result))
