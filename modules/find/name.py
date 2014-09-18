from core.vector import PhpCmd, ShellCmd
from core.module import Module
from core import messages
import random


class Name(Module):

    """Find files with matching name.

    Usage:
      find_name <name>

    """

    def initialize(self):

        self._register_info(
            {
                'name': 'Find files with matching name',
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            arguments =[
                'string'
            ],
            options={
                'rpath': '.',
                'equal': '',
                'case' : '',
                'recursion' : 'True',
                'vector' : 'php_recursive'
            },
            vector_argument = 'vector')

        self._register_vectors(
            [
            PhpCmd("""swp('${args['rpath']}');
function ckdir($df, $f) { return ($f!='.')&&($f!='..')&&@is_dir($df);} function match($f) {return preg_match("${ \"/%s/%s\" % ( '^%s$' % (args['string']) if args['equal'] else args['string'], 'i' if not args['case'] else '') }",$f);}
function swp($d){ $h=@opendir($d);while($f = readdir($h)) { $df=$d.'/'.$f; if(($f!='.')&&($f!='..')&&match($f))
print($df."\n"); if(@ckdir($df,$f)&&${False if (not args['recursion'] or args['recursion'].lower() == 'false') else True}) @swp($df); }
if($h) { @closedir($h); } }""", 'php_recursive'
            ),
            ShellCmd("""find ${args['rpath']} ${ '-maxdepth 1' if not args['recursion'] else '' } ${ '-name' if args['case'] else '-iname' } "${ '*%s*' % (args['string']) if not args['equal'] else args['string'] }" 2>/dev/null""", "sh_find")
            ]
        )


    def run(self, args):

        return self.vectors.get_result(args['vector'], { 'args' : args })
