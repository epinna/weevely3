"""
Override `error` method of `argparse.ArgumentParser`
in order to print the complete help on error.
"""
import argparse
import sys

SUPPRESS = argparse.SUPPRESS

class HelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
