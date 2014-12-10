from core.vectors import PhpCode
from core.module import Module
from core import messages
import random


class Extensions(Module):

    """Collect PHP and webserver extension list."""

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
            PhpCode("""
                $f='get_loaded_extensions';
                if(function_exists($f)&&is_callable($f))
                    foreach($f() as $o) print($o.PHP_EOL);
            """, 'php_extensions'),
            PhpCode("""
                $f='apache_get_modules';
                if(function_exists($f)&&is_callable($f))
                    foreach($f() as $o) print($o.PHP_EOL);
            """, 'apache_modules'),
            ]
        )

        self.register_arguments([
          { 'name' : '-info',
            'help' : 'Select modules or extensions',
            'choices' : self.vectors.get_names(),
            'nargs' : '+' }
        ])

    def run(self):

        result = self.vectors.get_results(
            names = self.args.get('info', [])
        )

        # Returns a string when a single information is requested,
        # else returns a dictionary containing all the results.
        info = self.args.get('info')
        if info and len(info) == 1:
            return result[info[0]]
        else:
            return result
