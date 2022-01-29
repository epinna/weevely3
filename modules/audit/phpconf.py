from core.vectors import PhpCode, ModuleExec
from core.module import Module
from core import messages
import re


class Phpconf(Module):
    """Audit PHP configuration."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

    def _check_user(self):

        user = ModuleExec('system_info', ['-info', 'whoami']).load_result_or_run('whoami')
        if not user: return messages.module_audit_phpconf.error

        result = user
        if 'win' in self.os_type: result += ': ' + messages.module_audit_phpconf.user_win_admin
        elif user == 'root': result += ': ' + messages.module_audit_phpconf.user_nix_root

        return result

    def _check_openbasedir(self):

        open_basedir = ModuleExec('system_info', ['-info', 'open_basedir']).load_result_or_run('open_basedir')
        if not open_basedir: return messages.module_audit_phpconf.basedir_unrestricted

        dir_sep = ModuleExec('system_info', ['-info', 'dir_sep']).load_result_or_run('dir_sep')
        if not self.os_type or not dir_sep: return messages.module_audit_phpconf.error

        path_sep = ';' if 'win' in self.os_type else ':'

        paths = open_basedir.split(path_sep)

        result = ''
        for path in paths:
            result += path + ': '
            if not path.endswith(dir_sep): result += ' ' + messages.module_audit_phpconf.basedir_no_slash
            elif path == '.': result += ' ' + messages.module_audit_phpconf.basedir_dot
            result += '\n'

        return result[:-1]

    def _check_features(self):

        features = [
            'expose_php',
            'file_uploads',
            'register_globals',
            'allow_url_fopen',
            'display_errors',
            'enable_dl',
            'safe_mode',
            'magic_quotes_gpc',
            'allow_url_include',
            'session.use_trans_sid'
        ]

        feat_found = PhpCode(
            """foreach ( Array("${ '", "'.join(features) }") as $f) if((bool)ini_get($f)) print($f. "\n");"""
        ).run({
            'features': features
        })

        result = []
        if feat_found:
            for feat in feat_found.split('\n'):
                feat_msg = 'feat_' + re.sub('[^a-zA-Z_]', '_', feat)
                if hasattr(messages.module_audit_phpconf, feat_msg):
                    result.append((feat, getattr(messages.module_audit_phpconf, feat_msg)))

        return result

    def _check_classes(self):

        classes = [
            'splFileObject',
            'COM',
            'Java'
        ]

        class_found = PhpCode(
            """foreach ( Array("${ '", "'.join(classes) }") as $f) if((bool)class_exists($f)) print($f. "\n");"""
        ).run({
            'classes': classes
        })

        result = []
        if class_found:
            for class_name in class_found.split('\n'):
                class_msg = 'class_' + re.sub('[^a-zA-Z_]', '_', class_name)
                if hasattr(messages.module_audit_phpconf, class_msg):
                    result.append((class_name, getattr(messages.module_audit_phpconf, class_msg)))

        return result

    def _check_functions(self):

        functions = {

            'info': [
                'apache_get_modules',
                'apache_get_version',
                'apache_getenv',
                'get_loaded_extensions',
                'phpinfo',
                'phpversion',
            ],
            'files': [
                'chgrp',
                'chmod',
                'chown',
                'copy',
                'link',
                'mkdir',
                'rename',
                'rmdir',
                'symlink',
                'touch',
                'unlink',
                'posix_mkfifo'
            ],
            'log': [
                'openlog',
                'syslog',
                'debugger_off',
                'debugger_on',
                'closelog'
            ],
            'proc_execution': [
                'exec',
                'passthru',
                'pcntl_exec',
                'popen',
                'proc_open',
                'shell_exec',
                'system',
                'dotnet_load'
            ],
            'proc_manipulation': [
                'apache_child_terminate',
                'apache_note',
                'apache_setenv',
                'dl',
                'proc_close',
                'proc_get_status',
                'proc_terminate',
                'proc_nice',
                'putenv',
                'virtual',
                'posix_kill',
                'posix_setpgid',
                'posix_setsid',
                'posix_setuid',
                'runkit_function_rename'
            ]
        }

        result = []

        for ftype, flist in functions.items():

            func_found = PhpCode((
                    "foreach ( Array(\"${ '\", \"'.join(functions) }\") as $f) " +
                    "if(function_exists($f)&&is_callable($f)) print($f. \"\\n\");"
            )).run({
                'functions': flist
            })

            if func_found:
                for func_name in func_found.split('\n'):
                    type_msg = 'func_' + re.sub('[^a-zA-Z_]', '_', ftype)
                    if hasattr(messages.module_audit_phpconf, type_msg):
                        msg = getattr(messages.module_audit_phpconf, type_msg)
                        if len(func_name) == 0:
                            msg = ''
                        result.append((func_name, msg))

        return result

    def run(self):

        self.os_type = ModuleExec('system_info', ['-info', 'os']).load_result_or_run('os')
        self.php_version = ModuleExec('system_info', ['-info', 'php_version']).load_result_or_run('php_version')

        results = [
                      ('Operating System',
                       self.os_type if self.os_type else 'Undetected'),
                      ('PHP version',
                       self.php_version if self.php_version else 'Undetected'),
                      ('User',
                       self._check_user()),
                      ('open_basedir',
                       self._check_openbasedir())
                  ] + self._check_features() + self._check_classes() + self._check_functions()

        return results
