from core.vectors import PhpCode
from core.module import Module

class Mail(Module):

    """Send Email"""

    aliases = [ 'Mail' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'appo'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : 'ToEmail', 'help' : 'Define the receiver of the email ', 'nargs' : '?', 'default' : '.' },
          { 'name' : 'FromEmail', 'help' : 'Define the sender of the email', 'nargs' : '?', 'default' : '.' },
          { 'name' : 'EmailSubject', 'help' : 'Define the subject of the email ', 'nargs' : '?', 'default' : '.' },
          { 'name' : 'EmailMessage', 'help' : 'Write message in " "', 'nargs' : '?', 'default' : '.' }
        ])

    def run(self):

        return PhpCode("""
        mail("${ToEmail}","${EmailSubject}","${EmailMessage}","From:${FromEmail}");
                """,
               ).run(self.args)

    def print_result(self, result):
        if result: log.info('\n'.join(result))
