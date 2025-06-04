import itertools

# Explode IP format 10.10.10.10-233
def ip_range(input_string):
    octets = input_string.split('.')
    chunks = [list(map(int, octet.split('-'))) for octet in octets]
    ranges = [list(range(c[0], c[1] + 1)) if len(c) == 2 else c for c in chunks]

    for address in itertools.product(*ranges):
        yield '.'.join(map(str, address))

# Explode port format 22,23-33
def port_range(input_string):
    return sum(
                (
                    (
                    list(range(*[int(j) + k for k, j in enumerate(i.split('-'))]))
                    if '-' in i else [int(i)]
                    )
                    for i in input_string.split(',')
                ), []
            )
