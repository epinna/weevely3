version = '4.0.1'

class generic:
    file_s_not_found = "File '%s' not found"
    error_creating_file_s_s = "Error creating file '%s': %s"
    error_loading_file_s_s = 'Error loading file \'%s\': %s'
    error_file_s_already_exists = 'Error file \'%s\' already exists'
    error_url_format = 'Expected URL format \'http(s)://host/agent.php\''
    error_parsing_command_s = 'Error parsing command: %s'
    weevely_s_error_s_usage = """
[+] weevely %s
[!] Error: %s

[+] Run terminal or command on the target
    weevely <URL> <password> [cmd]

[+] Recover an existing session
    weevely session <path> [cmd]

[+] Generate new agent
    weevely generate <password> <path>

"""

class sessions:
    set_module_s_s_s = '%s.%s = %s'
    set_s_s = '%s = %s'
    unset_module_s_s = '%s.%s is now unset'
    unset_s = '%s is now unset'
    error_loading_sessions = 'Session loading error'
    error_session_s_not_modified = 'Error setting session variable \'%s\''
    connection_info = """<%!
from urllib.parse import urlparse
%><%
if not host:
    urlparsed = urlparse(url)
    if urlparsed and urlparsed.netloc:
        hostname = urlparsed.netloc
    else:
        hostname = 'undefined host'
else:
    hostname = host
%>${'%s@' % user if user else ''}${hostname}${':%s' % path if path and path != '.' else ''}"""

class channels:
    error_loading_channel_s = 'Error loading channel \'%s\''
    error_proxy_format = 'Expected proxy URL format \'http|https|socks5|sock4://host:port\''

class terminal:
    backdoor_unavailable = 'Backdoor communication failed, check URL availability and password'
    welcome_no_shell = """
The system shell interpreter is not available in this session.
PHP code and modules execution are available. Use the following
command replacements to simulate an unrestricted shell.
"""
    help_no_shell = """
The system shell interpreter is not available in this session, use the
following command replacements to simulate a unrestricted shell.
"""
    welcome_to_s = """
[+] weevely ${version}

[+] Target:\t${conn_info}
[+] Session:\t${path}
% if default_shell:
[+] Shell:\t${ 'System shell' if default_shell == 'shell_sh' else 'PHP interpreter'}
% endif

[+] Browse the filesystem or execute commands starts the connection
[+] to the target. Type :help for more information.
"""
    set_usage = 'Set session variable (run :show to print). Usage:\n:set <variable> \'<value>\''
    unset_usage = 'Unset session variable (run :show to print). Usage:\n:unset <variable>'

class vectors:
    wrong_target_type = 'Wrong target operating system type'
    wrong_arguments_type = 'Wrong formatting argument type, a dictionary is required'
    wrong_postprocessing_type = 'Wrong postprocessing argument type, a callable function is required'
    wrong_payload_type = 'Wrong payload argument type, a string or a list of strings is required'
    wrong_condition_type = 'Wrong condition argument type, a callable function is required'
    wrong_store_name_type = 'Wrong argument type, a string with an argument name is required'

class vectorlist:
    vector_s_triggers_an_exc = 'Vector \'%s\' execution triggers an exception'

class module:
    error_setting_arguments_s = 'Error setting arguments: %s'
    argument_s_must_be_a_vector  = 'Argument \'%s\' must be a vector name'
    error_module_missing_description = 'Error, module description is missing'
    error_module_exec_error_s = 'Error, module execution triggered error \'%s\''
    error_init_method_required = 'Error, the init() method definition is required in Modules'
    module_s_exec_terminated = 'Module \'%s\' execution terminated'
    module_s_inactive = 'Module \'%s\' is inactive, skipped'
    error_choices_s_s_empty = 'Choices for \'%s\' argument \'%s\' is empty. Please check if vectors are declared before arguments.'
    running_the_alias_s = 'Shell interpreter unavailable, running the alias \'%s\''
    vector_s_not_support_arg_s_s = 'Vector \'%s\' does not support argument \'%s\' set to \'%s\''

class module_file_cd:
    failed_directory_change_to_s = "Failed cd '%s': no such directory or permission denied"
    error_getting_ossep = "Error getting remote directory separator"

class module_file_ls:
    failed_list_file_in_directory_s = "Failed list file in directory '%s': no such directory or permission denied"
    failed_list_file_in_directory_s_unknown = "Failed list file in directory '%s': unknown error"

class module_file_download:
    failed_download_file = "File download failed, please check remote path and permissions"
    skipping_md5_check = "Skipping MD5 check, the file integrity can't be checked"

class module_file_upload:
    error_content_lpath_required = "Error, argument 'lpath' or 'content' is required"
    failed_upload_file = "File upload failed, please check remote path and permissions"
    failed_md5_check = "Failed MD5 check, the integrity check is wrong or not available"

class module_file_edit:
    unmodified_file = "File unmodified, skipping upload"

class module_file_touch:
    error_invalid_timestamp_format = "Error, invalid timestamp format"
    error_source_timestamp_required = "Error, source timestamp is required."
    failed_touch_file = "File touch failed, please check remote path and permissions"

class module_sql_console:
    unexpected_response = "Unexpected response"
    check_credentials = "Check credentials and DB availability"
    no_data = "No data returned"
    missing_sql_trailer_s = 'Is the trailing comma missing at the end of the SQL statement \'%s\'?'

class module_sql_dump:
    sql_dump_failed_check_credentials = "SQL dump failed, check credentials and DB availability"
    sql_dump_saved_s = "SQL dump saved to '%s'"

class module_file_grep:
    failed_retrieve_info = "Failed retrieve file information, please check if the remote readable files exist"

class module_file_upload2web:
    failed_retrieve_info = "Failed retrieve web root information"
    failed_resolve_path = "Failed resolve path, please check remote path and permissions"
    error_s_not_under_webroot_s = "Error, \'%s\' is not under the web root folder \'%s\'"
    failed_search_writable_starting_s = "Error searching writable folder under '%s'."

class module_shell_php:
    error_404_remote_backdoor = 'The remote backdoor request triggers an error 404, check availability'
    error_500_executing = 'The remote script execution triggers an error 500, check script and payload integrity'
    error_URLError_network = 'Network error, unable to connect to the remote backdoor'
    error_proxy = 'Proxy error, unable to connect to the remote backdoor'
    missing_php_trailer_s = 'Is the trailing comma missing at the end of the PHP code \'%s\'?'
    error_i_executing = 'The request triggers the error %i, please verify running code'

class module_net_ifconfig:
    error_no_s_execution_result = 'Error, no \'%s\' execution result'
    error_parsing_s_execution_result = 'Error parsing \'%s\' execution result'
    error_interpeting_s_execution_result_s = 'Error interpreting \'%s\' execution result: \'%s\''
    failed_retrieve_info = "Failed retrieve ifconfig information"

class module_backdoor_tcp:
    error_parsing_connect_s = 'Error parsing hostname, connect manually to the shell on port %s'
    error_connecting_to_s_s_s = 'Error connecting to %s:%s: %s'

class module_backdoor_reversetcp:
    error_binding_socket_s = 'Error binding socket: \'%s\''
    error_timeout = 'Timeout error'
    reverse_shell_connected = 'Reverse shell connected, insert commands. Append semi-colon help to get the commands accepted.'

class module_audit_phpconf:
    not_enabled = 'Not enabled'
    enabled = 'Enabled'
    error = 'Error getting information'
    basedir_unrestricted = 'Unrestricted'
    basedir_dot = 'Set to \'.\', bypassable'
    basedir_no_slash = 'No trailing \'/\', bypassable'
    user_win_admin = 'Check this is not an administrative user'
    user_nix_root = 'User \'root\' can be abused'
    feat_expose_php = 'PHP configuration information exposed'
    feat_file_uploads = 'File upload enabled'
    feat_register_globals = 'Insecure variable manipulation enabled'
    feat_display_errors = 'Information display on error enabled'
    feat_enable_dl = 'Function dl() can be used to bypass restrictions'
    feat_safe_mode = 'Safe mode restrictions enabled'
    feat_magic_quotes_gpc = 'Insecure SQL injection protection enabled'
    feat_allow_url_include = 'Insecure inclusion of remote resources enabled'
    feat_session_use_trans_sid = 'Session IDs insecurely passed via URL'
    class_splFileObject = 'Class splFileObject can be used to bypass restrictions'
    class_COM = 'Class COM can be used to bypass restrictions'
    class_Java = 'Class Java can be used to bypass restrictions'
    func_info = 'Configuration exposed'
    func_files = 'Filesystem manipulation'
    func_log = 'Log tampering'
    func_proc_execution = 'Process execution'
    func_proc_manipulation = 'Process manipulation'

class module_net_curl:
    unexpected_response = 'Unexpected response, please check URL reachability'

class module_net_proxy:
    proxy_starting_s_i = 'Starting HTTP/HTTPS proxy at \'http://%s:%i\''
    proxy_set_proxy = 'Set the proxy to tunnel through the target. Visit \'http://weevely/\' to install the certificate'
    proxy_started_background = 'Proxy has been started in background and will shutdown at exit'
    proxy_started_foreground = 'Foreground proxy has been started, press Ctrl-C to stop it'

class module_net_phpproxy:
    phpproxy_installed_to_s_browser_to_s = 'PHP proxy installed to \'%s\', browse \'%s\' with your browser'
    proxy_script_removed = 'The PHP proxy script will be removed at weevely exit'
    proxy_script_manually_remove_s = 'Remove manually the PHP proxy script \'%s\''

class module_net_scan:
    unexpected_response = 'Unexpected response'

class module_file_archive:
    archive_type_not_set = 'Archive type not set and file extension not supported'
    error_extracting_s_file_needed = 'Error extracting %s, first remote file argument must contain the output file path'
    error_extracting_s_folder_needed = 'Error extracting %s, first remote file argument must contain the output folder path'
    remote_path_check_failed = "Remote path check failed, please check if exists and is readable"

class module_file_mount:
    httpfs_s_not_found = "HTTPfs binary '%s' not found, specify binary path or install it from 'https://github.com/cyrus-and/httpfs'"
    error_generating_agent = "Error generating HTTPfs PHP agent"
    failed_agent_upload = "Failed PHP agent upload"
    agent_installed_tutorial = """HTTPfs PHP agent installed remotely as ${agent_abs_path}.

Run the following commands in another console outside weevely to mount
and unmount the remote filesystem.

Mount locally a remote folder:
    ${httpfs_binary} mount '${agent_url}' <local folder> <remote folder>

Unmount it:
    fusermount -u <local folder>
"""
    httpfs_agent_removed = 'The PHP agent will be removed at weevely exit'
    httpfs_agent_manually_remove_s = 'Remove manually the PHP agent \'%s\''

class module_shell_su:
    error_su_executing = 'Error executing commands with su'

class module_shell_sh:
    error_sh_remote_shell = 'Error loading Sh remote shell'

class generate:
    error_agent_template_s_s = 'Error with agent template \'%s\': %s'
    error_obfuscator_template_s_s = 'Error with obfuscator template \'%s\': %s'
    generated_backdoor_with_password_s_in_s_size_i = 'Generated \'%s\' with password \'%s\' of %i byte size.'

class module_audit_disablefunctionbypass:
    error_sh_commands_enabled = 'Error, you can already execute system commands'
    error_mod_cgi_disabled = 'Error, mod_cgi module is not enabled'
    error_installing_htaccess = 'Error installing .htaccess'
    error_uploading_script_to_s = 'Error uploading CGI script to \'%s\''
    error_changing_s_mode = 'Error changing \'%s\' CGI script mode'
    error_s_unexpected_output = 'Error, \'%s\' doesn\'t execute, htaccess files aren\'t supported'
    run_s_skip_reinstalling = 'Run console without reinstalling with \':audit_disablefunctionbypass -just-run %s\''
    requests_not_obfuscated = 'Type \'quit\' to return to weevely shell. Requests are not obfuscated'
    cgi_installed_remove_s_s = 'After usage, use \':file_rm\' to remove \'%s\' and \'%s\''
