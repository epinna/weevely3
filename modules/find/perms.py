from core.vectors import PhpCmd, ShellCmd
from core.module import Module
from core.loggers import log
from core import messages
import random


class Perms(Module):

    """Find files with given write, read, or execute permission."""

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
              payload = """swp('${rpath}','${rpath}','${ type if type == 'd' or type == 'f' else '' }','${ '%s%s%s' % (('w' if writable else ''), ('r' if readable else ''), ('x' if executable else '') ) }','${ '1' if quit else '' }', ${not no_recursion});
function ckprint($df,$t,$a) { if(cktp($df,$t)&&@ckattr($df,$a)) { print($df.PHP_EOL); return True;}   }
function ckattr($df, $a) { $w=strstr($a,"w");$r=strstr($a,"r");$x=strstr($a,"x"); return ($a=='')||(!$w||is_writable($df))&&(!$r||is_readable($df))&&(!$x||is_executable($df)); }
function cktp($df, $t) { return ($t==''||($t=='f'&&@is_file($df))||($t=='d'&&@is_dir($df))); }
function swp($fdir, $d, $t, $a, $q, $r){
if($d==$fdir && ckprint($d,$t,$a) && ($q!="")) return;
$h=@opendir($d); while ($f = @readdir($h)) { if(substr($fdir,0,1)=='/') { $df='/'; } else { $df=''; }
$df.=join('/', array(trim($d, '/'), trim($f, '/')));
if(($f!='.')&&($f!='..')&&ckprint($df,$t,$a) && ($q!="")) return;
if(($f!='.')&&($f!='..')&&cktp($df,'d')&&$r){@swp($fdir, $df, $t, $a, $q, $r);}
} if($h) { closedir($h); } }""",
             name = 'php_recursive',
             postprocess = lambda x: x.split('\n')
            ),
            ShellCmd(
              payload = """find ${rpath} ${ '-maxdepth 1' if no_recursion else '' } ${ '-print -quit' if quit else '' } ${ '-writable' if writable else '' } ${ '-readable' if readable else '' } ${ '-executable' if executable else '' } ${ '-type %s' % (type) if type == 'd' or type == 'f' else '' } 2>/dev/null""",
              name = "sh_find",
              postprocess = lambda x: x.split('\n')
            )
            ]
        )

        self.register_arguments({
          'rpath' : { 'help' : 'Starting path' },
          '-quit' : { 'action' : 'store_true', 'default' : False, 'help' : 'Quit at first result' },
          '-writable' : { 'action' : 'store_true' },
          '-readable' : { 'action' : 'store_true' },
          '-executable' : { 'action' : 'store_true' },
          '-no-recursion' : { 'action' : 'store_true', 'default' : False },
          '-vector' : { 'choices' : self.vectors.get_names(), 'default' : 'php_recursive' },
        })

    def run(self, args):
        print args
        return self.vectors.get_result(args['vector'], args)

    def print_result(self, result):
        if result: log.info('\n'.join(result))
