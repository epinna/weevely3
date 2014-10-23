import random
import string
import subprocess
import itertools
import types
import prettytable
import re

def randstr(n=4, fixed=True, charset=None):

    if not n:
        return ''

    if not fixed:
        n = random.randint(1, n)

    if not charset:
        charset = string.letters + string.digits

    return ''.join(random.choice(charset) for x in range(n))


def sxor(s1, s2):
    return ''.join(chr(ord(a) ^ ord(b))
                   for a, b in zip(s1, itertools.cycle(s2)))


def divide(str, min_size, max_size, split_size):
    it = iter(str)
    size = len(str)
    for i in range(split_size - 1, 0, -1):
        s = random.randint(min_size, size - max_size * i)
        yield ''.join(itertools.islice(it, 0, s))
        size -= s
    yield ''.join(it)


def stringify(data, table_border = True):

    # TODO: Check that is prettytable-0.7.2 that supports the
    # dynamic table columns number setting. Version 0.5 does not.

    output = ''

    # Empty outputs. False is probably a good output value
    if data and not data:
        output = ''
    else:

        table = prettytable.PrettyTable()

        # List outputs.
        if isinstance(data, (types.ListType, types.TupleType)):

            if len(data) > 0:

                columns_num = 1
                if isinstance(data[0], (types.ListType, types.TupleType)):
                    columns_num = len(data[0])

                for row in data:
                    if isinstance(row, (types.ListType, types.TupleType)):
                        table.add_row(row)
                    else:
                        table.add_row([row])

        # Dict outputs are display as tables
        elif isinstance(data, types.DictType) and data:

            # Populate the rows
            randomitem = next(data.itervalues())
            if isinstance(randomitem, (types.ListType, types.TupleType)):
                for field in data:
                    table.add_row([field] + data[field])
            else:
                for field in data:
                    table.add_row([field, str(data[field])])

        # Else, try to stringify
        else:
            output = str(data)

        if not output:
            table.header = False
            table.align = 'l'
            table.border = table_border
            output = table.get_string()

    return output


def getstatusoutput(cmd):
    """
    Return (status, output) of executing cmd in a shell.
    This new implementation should work on all platforms.
    """
    pipe = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = str.join("", pipe.stdout.readlines())
    sts = pipe.wait()
    if sts is None:
        sts = 0
    return sts, output


def shorten_string(body, keep_header = 0, keep_trailer = 0):
    """
    Smartly shorten a given string.
    """

    # Cut header
    if (keep_header
        and not keep_trailer
        and len(body) > keep_header):
            return '..%s' % body[:keep_header]

    # Cut footer
    if (keep_trailer
        and not keep_header
        and len(body) > keep_trailer):
            return '..%s' % body[-keep_header:]

    if (keep_header
        and keep_trailer
        and len(body) > keep_header + keep_trailer):
            return '%s .. %s' % (body[:keep_header], body[-keep_trailer:])

    return body
