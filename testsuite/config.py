# Weevely testsuite configuration

# To get started with the testsuite, create a dedicated folder
# in your web enviroinment and set permissions in order to give
# total write, read and execute permissions to the web user.
#
# Then set the `script_folder` variable to the dedicated folder path
# and set the `script_folder_url` variable to the corresponding URL
# exposed through the web service.
#
# Example:
# $ sudo mkdir /var/www/environment
# $ sudo chown www-data:www-data /var/www/environment
#
script_folder = '/var/www/environment/'
script_folder_url = 'http://localhost/environment/'
#
# If your web server is properly exposing the `script_folder_url`,
# executing the command `python -m unittest discover` from the
# weevely root folder should give the following output.
#
# $ python -m unittest discover
# ...garbage...
# ----------------------------------------------------------------------
# Ran 31 tests in 26.780s
# OK (skipped=4)
# $

#
# The following cmd_env_* commands are used to setup the
# test enviroinment. Feel free to modify with ssh or other commands
# to setup remote enviroinments.
#
cmd_env_move_s_s = 'mv %s %s'
cmd_env_chmod_s_s = 'chmod %s %s'
cmd_env_mkdir_s = 'mkdir %s'
cmd_env_rmdir_s = 'rmdir %s'
cmd_env_remove_s = 'rm -f %s'
cmd_env_content_s_to_s = 'echo -n "%s" > %s'

# Set to True to enable debug prints
debug = False

# This option is used by test_channels to reduce the requests
test_generated_test_all_agents = False
