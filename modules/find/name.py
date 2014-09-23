from core.vector import PhpCmd, ShellCmd
from core.module import Module
from core import messages
import random


class Name(Module):

    """Find files with matching name."""

    def init(self):

        self._register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            mandatory = [
                'string'
            ],
            optional = {
                'rpath': '.',
                'contains': '',
                'case' : '',
                'recursive' : 'True',
                'vector' : 'php_recursive'
            },
            bind_to_vectors = 'vector')

        self._register_vectors(
            [
            PhpCmd("""swp('${args['rpath']}');
function ckdir($df, $f) { return ($f!='.')&&($f!='..')&&@is_dir($df);} function match($f) {return preg_match("${ \"/%s/%s\" % ( '^%s$' % (args['string']) if not args['contains'] else args['string'], 'i' if not args['case'] else '') }",$f);}
function swp($d){ $h=@opendir($d);while($f = readdir($h)) { $df=$d.'/'.$f; if(($f!='.')&&($f!='..')&&match($f))
print($df."\n"); if(@ckdir($df,$f)&&${False if (not args['recursive'] or args['recursive'].lower() == 'false') else True}) @swp($df); }
if($h) { @closedir($h); } }""", 'php_recursive'
            ),
            ShellCmd("""find ${args['rpath']} ${ '-maxdepth 1' if not args['recursive'] else '' } ${ '-name' if args['case'] else '-iname' } "${ '*%s*' % (args['string']) if args['contains'] else args['string'] }" 2>/dev/null""", "sh_find")
            ]
        )

    def run(self, args):
        return self.vectors.get_result(args['vector'], { 'args' : args })
