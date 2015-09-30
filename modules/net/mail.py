from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module
from core import modules

class Mail(Module):

    """Send mail."""

    aliases = [ 'mail' ]

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
          { 'name' : 'to', 'help' : 'Receiver, or receivers of the mail' },
          { 'name' : 'subject', 'help' : 'Subject of the mail to be sent. ' },
          { 'name' : 'message', 'help' : 'Message to be sent. ( Write message in " " ) ' },
          { 'name' : 'sender', 'help' : 'Set sender of the mail. ' }
        ])

    def run(self):

        return PhpCode("""(mail('${to}', '${subject}', '${message}', 'From: ${sender}') && print(1)) || print(0);""",
                        postprocess = lambda x: True if x == '1' else False
                        ).run(self.args)
