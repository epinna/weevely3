from core.vectors import ShellCmd
from core.module import Module

# https://staaldraad.github.io/2017/12/20/netstat-without-netstat/
netstat_without_netstat = "grep -v 'rem_address' /proc/net/tcp | awk 'function hextodec(str,ret,n,i,k,c){ret=0;n=length(str);for(i=1;i<=n;i++){c=tolower(substr(str,i,1));k=index(\"123456789abcdef\",c);ret=ret*16+k;}return ret} {x=hextodec(substr($2,index($2,\":\")-2,2));for(i=5;i>0;i-=2)x=x\".\"hextodec(substr($2,i,2))}{print x\":\"hextodec(substr($2,index($2,\":\")+1,4))}' | grep -v ':0' | sort -u"

class Fingerprint(Module):
    """Find a few basic information about target"""

    def init(self):
        self.register_info(
            {
                'author': [
                    'ZanyMonk'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            {'name': 'rpath', 'help': 'Remote starting path (default: /)', 'default': '/', 'nargs': '?'},
        ])

    def run(self):
        output = []
        tests = {
            'Current user': 'id',
            'Local time': 'date',
            'Hostname': 'uname -n',
            'Address(es)': 'hostname -I',
            'Kernel': 'echo $(uname -s) $(uname -n) $(uname -r) $(uname -v)',
            'Processor': "cat /proc/cpuinfo | grep 'model name' | head -n1 | sed 's/.*: //'",
            'Memory usage': 'free -h',
            'Disk usage': 'df -h',
            'Listening ports': f"ss -tlp || netstat -laputn | grep LISTEN || echo '(Without netstat)' && {netstat_without_netstat}",
        }

        for title in tests:
            result = ShellCmd(
                payload=tests[title],
                arguments=[
                    "-stderr_redirection",
                    " 2>/dev/null",
                ]).run(self.args)

            output.append([title, result if len(result) else '[Empty]'])

        # return output.split('\n')
        return output