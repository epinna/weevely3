import random
import string
import itertools

str2hex = lambda x: "\\x" + "\\x".join([hex(ord(c))[2:].zfill(2) for c in x])

def randstr(n=4, fixed=True, charset=None):

    if not n:
        return b''

    if not fixed:
        n = random.randint(1, n)

    if not charset:
        charset = string.ascii_letters + string.digits

    return ''.join(random.choice(charset) for x in range(n)).encode('utf-8')

def divide(data, min_size, max_size, split_size):

    it = iter(data)
    size = len(data)

    for i in range(split_size - 1, 0, -1):
        s = random.randint(min_size, size - max_size * i)
        yield bytearray(itertools.islice(it, 0, s))
        size -= s
    yield bytearray(it)

def sxor(s1, s2):
    return bytearray(
        a ^ b
        for a, b in zip(s1, itertools.cycle(s2))
    )

def pollute(data, charset, frequency=0.3):

    str_encoded = ''
    for char in data:
        if random.random() < frequency:
            str_encoded += randstr(1, True, charset) + char
        else:
            str_encoded += char

    return str_encoded

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]
