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


        self.register_vectors(
            [
            PhpCmd(
              payload = """swp('${rpath}');
function ckdir($df, $f) { return ($f!='.')&&($f!='..')&&@is_dir($df);} function match($f) {return preg_match("${ \"/%s/%s\" % ( '^%s$' % (expression) if not contains else expression, 'i' if not case else '') }",$f);}
function swp($d){ $h=@opendir($d);while($f = readdir($h)) { $df=$d.'/'.$f; if(($f!='.')&&($f!='..')&&match($f))
print($df.PHP_EOL); if(@ckdir($df,$f)&&${not no_recursion}) @swp($df); }
if($h) { @closedir($h); } }""",
              name = 'php_recursive',
              postprocess = lambda x: x.split('\n')
            ),
            ShellCmd(
              payload = """find ${rpath} ${ '-maxdepth 1' if no_recursion else '' } ${ '-name' if case else '-iname' } "${ '*%s*' % (expression) if contains else expression }" 2>/dev/null""",
              name = "sh_find",
              postprocess = lambda x: x.split('\n')
            )
            ]
        )

        self.register_arguments({
          'expression' : {  'help' : 'Expression to mach with the file names' },
          'rpath' : { 'help' : 'Starting path' },
          '-contains' : { 'action' : 'store_true', 'default' : False },
          '-case' : { 'action' : 'store_true', 'default' : False },
          '-no-recursion' : { 'action' : 'store_true', 'default' : False },
          '-vector' : { 'choices' : self.vectors.get_names(), 'default' : 'php_recursive' },
        })

    def run(self, args):
        return self.vectors.get_result(args['vector'], args)

    def print_result(self, result):
        if result: log.info('\n'.join(result))
