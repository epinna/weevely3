import re

from weevely.core import messages
from weevely.core.loggers import log
from weevely.core.module import Module
from weevely.core.vectors import ModuleExec
from weevely.core.vectors import Os
from weevely.core.vectors import ShellCmd
from weevely.utils.ipaddr import IPNetwork


class Ifconfig(Module):
    """Get network interfaces addresses."""

    aliases = ["ifconfig"]

    def init(self):
        self.register_info({"author": ["Emilio Pinna"], "license": "GPLv3"})

    def _get_ifconfig_result(self, ifconfig_path):
        result = ShellCmd(ifconfig_path, target=Os.NIX).run()

        if not result:
            log.debug(messages.module_net_ifconfig.error_no_s_execution_result % ifconfig_path)
            return {}

        ifaces = re.findall(r"^(\S+).*?inet addr:(\S+).*?Mask:(\S+)", result, re.S | re.M)

        if not ifaces:
            log.debug(messages.module_net_ifconfig.error_parsing_s_execution_result % ifconfig_path)
            return {}

        networks = {}

        for iface in ifaces:
            try:
                networks[iface[0]] = IPNetwork("%s/%s" % (iface[1], iface[2]))
            except Exception as e:
                log.debug(messages.module_net_ifconfig.error_interpeting_s_execution_result_s % (ifconfig_path, str(e)))
                networks[iface[0]] = IPNetwork("%s/%s" % (iface[1], iface[2]))
            except Exception as e:
                log.debug(messages.module_net_ifconfig.error_interpeting_s_execution_result_s % (ifconfig_path, str(e)))

        return networks

    def run(self, **kwargs):
        # Call raw ifconfig from $PATH and return it
        result = self._get_ifconfig_result("ifconfig")
        if result:
            return result

        # Is usually not in $PATH cause is suid. Enumerating paths.
        ifconfig_paths = ModuleExec(
            "file_enum",
            [
                "%sifconfig" % x
                for x in ["/sbin/", "/bin/", "/usr/bin/", "/usr/sbin/", "/usr/local/bin/", "/usr/local/sbin/"]
            ],
        ).run()

        for path in ifconfig_paths:
            result = self._get_ifconfig_result(path)
            if result:
                return result

        log.warn(messages.module_net_ifconfig.failed_retrieve_info)
