from core.vectors import PhpFile
from core.module import Module
from core.argparsers import SUPPRESS
from core import modules
from core.loggers import log
from core import messages
import utils
import os

class Scan(Module):

    """TCP Port scan."""

    aliases = [ 'nmap' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            PhpFile(
              payload_path = os.path.join(self.folder, 'fsockopen.tpl'),
              name = 'fsockopen',
            )
            ]
        )

        self.register_arguments([
          { 'name' : 'addresses', 'help' : 'IPs or interface e.g. 10.1.1.1,10.1.1.2 or 10.1.1.1-254 or 10.1.1.1/255.255.255.0 or eth0' },
          { 'name' : 'ports', 'help' : 'Ports e.g. 80,8080 or 80,8080-9090' },
          { 'name' : '-timeout', 'help' : 'Connection timeout', 'type' : int, 'default' : 1 },
          { 'name' : '-print', 'action' : 'store_true', 'default' : False, 'help' : 'Print closed and filtered ports' },
          { 'name' : '-addresses-per-request', 'help' : SUPPRESS, 'type' : int, 'default' : 10 },
          { 'name' : '-ports-per-request', 'help' : SUPPRESS, 'type' : int, 'default' : 5 },
        ])

    def run(self):

        ## Address handling

        # Explode every single IP or network starting from
        # format IP1,IP2-IP3,IP/MASK,..
        IPs = []
        for ip_or_network in self.args['addresses'].split(','):

            if ip_or_network.count('-') == 1:
                # If there is a dash, explode
                IPs += list(
                    utils.iputil.ip_range(ip_or_network)
                )
            elif ip_or_network.count('/') == 1:
                # If there is a /, too
                IPs += [
                    str(utils.ipaddr.IPAddress(ip)) for ip in
                    utils.ipaddr.IPNetwork(ip_or_network)
                ]
            else:
                IPs.append(ip_or_network)

        ## Port handling
        prts = utils.iputil.port_range(self.args['ports'])

        results_string = ''

        for ips_chunk in list(utils.strings.chunks(IPs, self.args['addresses_per_request'])):
            for prts_chunk in list(utils.strings.chunks(prts, self.args['ports_per_request'])):

                results_string += self.vectors.get_result(
                    name = 'fsockopen',
                    format_args = {
                                    'ips' : ips_chunk,
                                    'prts' : prts_chunk,
                                    'timeout' : self.args['timeout'] }
                )

                log.warn('Scanning addresses %s-%s:%i-%i' % (
                            ips_chunk[0], ips_chunk[-1],
                            prts_chunk[0], prts_chunk[-1]
                        )
                )

        # Crappy output handling

        result = []
        for result_string in results_string.split('\n'):

            addr_string_splitted = result_string.split(' ')

            if addr_string_splitted[0] == 'OPN':
                address = addr_string_splitted[1]
                error = 'OPEN'
            elif addr_string_splitted[0] == 'ERR':
                address = addr_string_splitted[1]
                error = '%s (%s)' % (
                            ' '.join(addr_string_splitted[2:-1]),
                            addr_string_splitted[-1]
                        )
            else:
                log.debug(
                    messages.module_net_scan.unexpected_response
                )
                continue

            if self.args.get('print'):
                result.append((address, error))
            elif error == 'OPEN':
                result.append(address)

        return result
