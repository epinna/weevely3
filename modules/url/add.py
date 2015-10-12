from core.module import Module
from core.channels.channel import Channel
import re
import os

class Add(Module):

    """Add a url/password pair to weevely access."""

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
            { 'name' : 'url' },
            { 'name' : 'password' }
        ])

    def run(self):
	cchannel = os.path.join(os.path.dirname(self.session['path']),"channels")
	Channel.add_to_chan(self.args["url"],self.args["password"],cchannel)
        return "Entry point "+self.args["url"]+":"+self.args["password"]+" added" 
