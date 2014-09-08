from core.vector import Os, Vector
from core.module import Module
from core import messages
from core.loggers import log
import random
import hashlib


class Upload(Module):

    """Upload file to remote filesystem.

    Usage:
      file_upload <lfile> <rfile>

    """

    def initialize(self):

        self._register_infos(
            {
                'name': 'Change directory',
                'description': __doc__,
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self._register_arguments(
            # Declare mandatory arguments
            arguments=[
                'lfile',
                'rfile',
                'vector'
            ],
            # Declare additional options
            options={
                'content': ''
            },
            vector_argument = 'vector')
            
        self._register_vectors(
            [
            Vector(
              "file_put_contents('${args['rpath']}', base64_decode(${content}), FILE_APPEND);",
              name = 'file_put_contents'
              ),
              
            Vector(
              """'$h = fopen("${args['rpath']}", "a+"); fwrite($h, base64_decode(${content}); fclose($h);""",
              name = "fwrite"
              )
            ]
        )

    def setup(self, args):

        # Load local file
        content = args.get('content')
        if not content:

            lpath = args.get('lpath')
            
            try:
                content = open(lpath, 'r').read()
            except Exception, e:
                log.warning(
                  messages.generic.error_loading_file_s_s % (lpath, str(e)))
                return False

        content_md5 = hashlib.md5(content).hexdigest()

        # Check remote file existance


        #~ folder = Vector("""@chdir("${args['dir']}") && print(getcwd());""", "chdir").run({ 'args' : args })
#~ 
        #~ if folder:
            #~ # Store cwd used by other modules
            #~ self._store_result('cwd', folder)
        #~ else:
            #~ log.warning(
                #~ messages.module_file_cd.failed_directory_change_to_s %
                #~ (args['dir']))        

    def run(self, args):
        

        pass
