from core.module import Module
from core.channels.channel import Channel
import re
import os

class Del(Module):

    """Remove a weevely entry point."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Jack Lean'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            { 'name' : 'url' }
        ])

    def run(self):
	cchannel = os.path.join(os.path.dirname(self.session['path']),"channels")
    	Channel.del_from_chanFile(self.args["url"], cchannel)
        return "Entry point "+self.args["url"]+" removed" 
