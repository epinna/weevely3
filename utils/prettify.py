import prettytable
import types

def tablify(data, table_border = True):

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
                    if not row:
                        continue
                        
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

def shorten(body, keep_header = 0, keep_trailer = 0):
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
