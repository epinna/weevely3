
class generic:
    file_s_not_found = "File '%s' not found"
    error_creating_file_s_s = "Error creating file '%s': %s"
    error_missing_arguments_s = 'Error missing arguments %s'
    error_loading_file_s_s = 'Error loading file \'%s\': %s'


class sessions:
    error_loading_sessions = 'Error loading sessions'


class channels:
    error_loading_channel_s = 'Error loading channel \'%s\''


class terminal:
    backdoor_unavailable = 'Backdoor communication failed: please check URL reachability and password'


class stegareferrer:
    error_generating_id = 'Error generating id, payload too long?'
    error_password_hash = 'Error generating trigger, please use another password'
    error_language_start_letter_s = 'Error, at least one language must start with the letter \'%s\''
    error_chunk_position_i_s = 'Error chunk position %i is not indexable, delete template \'%s\''


class vectors:
    wrong_target_type = 'Wrong target operating system type'
    wrong_arguments_type = 'Wrong formatting argument type, a dictionary is required'
    wrong_postprocessing_type = 'Wrong postprocessing argument type, a callable function is required'

class module:
    default_vector_not_set = 'Default vector is not set'


class module_file_cd:
    failed_directory_change_to_s = "Failed working directory change to '%s': no such directory or permission denied"
    error_getting_ossep = "Error getting remote directory separator"


class module_file_ls:
    failed_list_file_in_directory_s = "Failed list file in directory '%s': no such directory or permission denied"
    failed_list_file_in_directory_s_unknown = "Failed list file in directory '%s': unknown error"


class module_shell_php:
    error_404_remote_backdoor = 'The remote backdoor request triggers an error 404, please verify its availability'
    error_500_executing = 'The remote script execution triggers an error 500, please verify script integrity and sent payload correctness'
    missing_php_trailer_s = 'Is the trailing comma missing at the end of the sent payload \'%s\'?'
    error_i_executing = 'The request triggers the error %i, please verify running code'


class module_shell_sh:
    error_sh_remote_shell = 'Error loading Sh remote shell'


class generate:
    error_agent_template_s_s = 'Error with agent template \'%s\': %s'
    error_obfuscator_template_s_s = 'Error with obfuscator template \'%s\': %s'
    generated_backdoor_with_password_s_in_s_size_i = 'Generated backdoor with password \'%s\' in \'%s\' of %i byte size.'
