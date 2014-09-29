from core.vectors import PhpCmd, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random


class Name(Module):

    """Find files with matching name."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments(
            mandatory = [
                'expression'
            ],
            optional = {
                'rpath': '.',
                'contains': '',
                'case' : '',
                'recursive' : 'True',
                'vector' : 'php_recursive'
            },
            bind_to_vectors = 'vector')

        self.register_vectors(
            [
            PhpCmd(
              payload = """swp('${rpath}');
function ckdir($df, $f) { return ($f!='.')&&($f!='..')&&@is_dir($df);} function match($f) {return preg_match("${ \"/%s/%s\" % ( '^%s$' % (expression) if not contains else expression, 'i' if not case else '') }",$f);}
function swp($d){ $h=@opendir($d);while($f = readdir($h)) { $df=$d.'/'.$f; if(($f!='.')&&($f!='..')&&match($f))
print($df."\n"); if(@ckdir($df,$f)&&${False if (not recursive or recursive.lower() == 'false') else True}) @swp($df); }
if($h) { @closedir($h); } }""", 
              name = 'php_recursive',
              postprocess = lambda x: x.split('\n')
            ),
            ShellCmd(
              payload = """find ${rpath} ${ '-maxdepth 1' if not recursive else '' } ${ '-name' if case else '-iname' } "${ '*%s*' % (expression) if contains else expression }" 2>/dev/null""", 
              name = "sh_find",
              postprocess = lambda x: x.split('\n')
            )
            ]
        )

    def run(self, args):
        return self.vectors.get_result(args['vector'], args)

    def print_result(self, result):
        if result: log.info('\n'.join(result))
