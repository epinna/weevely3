
class generic:
    file_s_not_found = "file '%s' not found"
    error_creating_file_s_s = "error creating file '%s': %s"
    error_missing_arguments_s = 'error missing arguments %s'
    error_loading_file_s_s = 'error loading file \'%s\': %s'

class sessions:
    error_loading_sessions = 'error loading sessions'
	# TODO: use generic one
    
class channels:
    error_loading_channel_s = 'error loading channel \'%s\''

class terminal:
    backdoor_unavailable = 'backdoor is unavailable, please check if weevely3 agent is available at URL and if password is correct.'
    
class stegareferrer:
	# TODO: review and delete unused ones
    error_generating_id = 'error generating id, payload too long?'
    error_password_hash = 'error generating trigger, please use another password'
    error_language_start_letter_s = 'error, at least one language must start with the letter \'%s\''
    error_chunk_position_i_s = 'error chunk position %i is not indexable, delete template \'%s\''
    
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
