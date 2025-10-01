import glob
import os

from . import config


loaded = {}
loaded_tree = {}


def load_modules(session):
    """Load all modules"""

    modules_paths = glob.glob(f"{config.weevely_path}/modules/*/[a-z]*py")

    for module_path in modules_paths:
        module_group, module_filename = module_path.split(os.sep)[-2:]
        module_name = os.path.splitext(module_filename)[0]
        classname = module_name.capitalize()

        # Import module
        module = __import__(f"weevely.modules.{module_group}.{module_name}", fromlist=["*"])

        # Check if the module support folder exists
        folder = module_path.replace(module_filename, "_%s" % module_name)

        # Init class, passing current terminal instance and module name
        module_class = getattr(module, classname)(session, f"{module_group}_{module_name}", folder)

        loaded[f"{module_group}_{module_name}"] = module_class

        # Keep the tree in a dict of strings in the form
        # `{ 'group1' : [ 'mod1', 'mod2' ] }`
        tree_group = loaded_tree.get(module_group)
        if not tree_group:
            loaded_tree[module_group] = []
        loaded_tree[module_group].append(f"{module_group}_{module_name}")
