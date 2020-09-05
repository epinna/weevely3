import prettytable
import types

def tablify(data, table_border = True, header=False):

    # TODO: Check that is prettytable-0.7.2 that supports the
    # dynamic table columns number setting. Version 0.5 does not.

    output = ''

    # Empty outputs. False is probably a good output value
    if data is not False and not data:
        output = ''
    else:

        table = prettytable.PrettyTable()
        if header and type(data) is list:
            table.field_names = data.pop(0)
            table.header = True
        else:
            table.header = False
        # List outputs.
        if isinstance(data, (list, tuple)):

            if len(data) > 0:

                columns_num = 1
                if isinstance(data[0], (list, tuple)):
                    columns_num = len(data[0])

                for row in data:
                    if not row:
                        continue

                    if isinstance(row, (list, tuple)):
                        table.add_row(row)
                    else:
                        table.add_row([row])

        # Dict outputs are display as tables
        elif isinstance(data, dict) and data:

            # Populate the rows
            randomitem = next(iter(list(data.values())))
            if isinstance(randomitem, (list, tuple)):
                for field in data:
                    table.add_row([field] + data[field])
            else:
                for field in data:
                    table.add_row([field, str(data[field])])

        # Else, try to stringify
        else:

            # Normalize byte-like objects
            try:
                data = data.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                pass

            output = str(data)

        if not output:
            table.align = 'l'
            table.border = table_border
            output = table.get_string()

    return output

def shorten(body, keep_header = 0, keep_trailer = 0):
    """
    Smartly shorten a given string.
    """

    # Normalize byte-like objects
    try:
        body = body.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        pass

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


def format_size(size, suffix='o'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1000.0:
            return "%.3G%s%s" % (size, unit, suffix)
        size /= 1000.0
    return "%.3G%s%s" % (size, 'Y', suffix)
