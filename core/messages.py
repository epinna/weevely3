
class generic:
    file_s_not_found = "file '%s' not found"
    error_creating_file_s_s = "error creating file '%s': %s"
    error_missing_arguments_s = 'error missing arguments %s'

class sessions:
    error_loading_sessions = 'error loading sessions'
    error_loading_file_s_s = 'error loading file \'%s\': %s'
    
class channels:
    error_loading_channel_s = 'error loading channel \'%s\''

class terminal:
    backdoor_unavailable = 'backdoor is unavailable, please check if weevely3 agent is available at URL and if password is correct.'
    
class stegareferrer:
    error_loading_referrers_s_s = 'error loading referrers templates \'%s\': %s' 
    error_conflict_url_key = 'conflict between encoded url and keys, skipping template' 
    
class vectors:
    wrong_target_type = 'wrong target operating system type'
    default_vector_not_set = 'default vector is not set'
    
class module_file_cd:
    failed_directory_change_to_s = "failed working directory change to '%s': no such directory or permission denied"
    error_getting_ossep = "error getting remote directory separator"

class module_file_ls:
    failed_list_file_in_directory_s = "failed list file in directory '%s': no such directory or permission denied"
    failed_list_file_in_directory_s_unknown = "failed list file in directory '%s': unknown error"

class module_shell_php:
    error_php_remote_shell = 'error loading PHP remote shell'
    
class module_shell_sh:
    error_sh_remote_shell = 'error loading Sh remote shell' 
    
class generate:
    error_agent_template_s_s = 'error with agent template \'%s\': %s'
    error_obfuscator_template_s_s = 'error with obfuscator template \'%s\': %s'
    generated_backdoor_with_password_s_in_s = 'generated backdoor with password \'%s\' in \'%s\''