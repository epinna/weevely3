from core.module import Module
from core.channels.channel import Channel
import re
import os

class List(Module):

    """List registered weevely entry points."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Jack Lean'
                ],
                'license': 'GPLv3'
            }
        )

    def run(self):
	cchannel = os.path.join(os.path.dirname(self.session['path']),"channels")
	with open(cchannel,"r") as f:
		res = f.read()
        return "Entry points :\n"+res 
