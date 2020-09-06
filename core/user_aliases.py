from core.config import base_path
from core.loggers import log

import atexit


class UserAliases:
    """Handles user-defined aliases stored in a text file"""

    def __init__(self, filepath=None):
        self.aliases = {}
        self.path = filepath if filepath else base_path + 'aliases'

        if self.path is not None:
            self.load_from_file(self.path)

        atexit.register(self._session_save_atexit)

    def _session_save_atexit(self):
        with open(self.path, 'w') as f:
            f.writelines(
                ['{}={}\n'.format(alias, code) for alias, code in self.aliases.items()]
            )
            f.close()

    def load(self, aliases):
        """Loads aliases from a newline-delimited string"""
        sep = '='
        for line in aliases.split('\n'):
            splitted = line.split(sep)
            alias = splitted[0]
            if alias in (None, ''):
                continue
            code = sep.join(splitted[1:])

            self.set(alias, code)

    def load_from_file(self, filename):
        """Loads aliases from a file. One alias by line (format: name=code)"""
        sep = '='
        with open(filename, 'a+') as f:
            f.seek(0)

            for line in f:
                splitted = line.rstrip().split(sep)
                alias = splitted[0]
                if alias in (None, ''):
                    continue
                code = sep.join(splitted[1:])

                self.set(alias, code)

            f.close()

    def print_to_user(self, name=None):
        if name is None:
            for alias, code in self.aliases.items():
                print('{} = {}'.format(alias, code))
        else:
            code = self.get(name)
            if code is None:
                log.warning('alias {} does not exist.'.format(name))
            else:
                print('alias {} = {}'.format(name, code))

    def set(self, alias, code):
        """User-called function which sets an alias"""
        if not alias.isalpha():
            log.warning('"{}" is not a valid alias name. Use only letters.'.format(alias))
            return

        self.aliases[alias] = code

    def unset(self, alias):
        """User-called function which removes an alias"""
        if alias not in self.aliases:
            log.warning('alias {} does not exist.'.format(name))

        self.aliases.pop(alias)

    def get(self, alias):
        if alias not in self.aliases:
            return None

        return self.aliases[alias]

    def apply(self, line):
        """Applies alias transformation to the given command line.
        If the command line matches no alias, it's returned untouched."""

        argv = line.split(' ')

        if len(argv) < 1:
            return line

        aliased = self.get(argv[0])

        if aliased is None:
            aliased = argv[0]

        return ' '.join([aliased] +argv[1:])