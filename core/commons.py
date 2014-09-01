import random
import string
import subprocess
import itertools
import types
import prettytable


def chunks_equal(l, n):
    """ Yield n successive chunks from l.
    """
    newn = int(len(l) / n)
    for i in xrange(0, n - 1):
        yield l[i * newn:i * newn + newn]
    yield l[n * newn - newn:]


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


def stringify(data):

    output = ''

    # Empty outputs. False is probably a good output value
    if data and not data:
        output = ''
    else:

        table = prettytable.PrettyTable()

        # List outputs.
        if isinstance(data, types.ListType):

            if len(data) > 0:

                columns_num = 1
                if isinstance(data[0], types.ListType):
                    columns_num = len(data[0])

                for row in data:
                    if isinstance(row, types.ListType):
                        table.add_row(row)
                    else:
                        table.add_row([row])

                output = table.get_string()

        # Dict outputs are display as tables
        elif isinstance(data, types.DictType) and data:

            # Populate the rows
            randomitem = next(data.itervalues())
            if isinstance(randomitem, types.ListType):
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
            output = table.get_string()

    return output


def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell."""
    """This new implementation should work on all platforms."""
    pipe = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = str.join("", pipe.stdout.readlines())
    sts = pipe.wait()
    if sts is None:
        sts = 0
    return sts, output
