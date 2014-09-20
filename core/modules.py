import glob
import os

loaded = {}

def load_modules(session):
    """ Load all modules """

    modules_paths = glob.glob('modules/*/[a-z]*py')

    for module_path in modules_paths:

        module_group, module_filename = module_path.split(os.sep)[-2:]
        module_name = os.path.splitext(module_filename)[0]
        classname = module_name.capitalize()

        # Import module
        module = __import__(
            'modules.%s.%s' %
            (module_group, module_name), fromlist=["*"])
        # init class, passing current terminal instance and module
        # name
        module_class = getattr(
            module, classname)(
            session, '%s_%s' %
            (module_group, module_name))

        loaded['%s_%s' %
            (module_group, module_name)] = module_class
