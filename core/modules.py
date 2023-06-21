import glob
import os

import click

from core import config

loaded = {}
loaded_tree = {}
plugin_folder = os.path.join(os.path.dirname(__file__), 'modules')


class Manager(click.Group):

    def __init__(self, **attrs):
        attrs['invoke_without_command'] = True
        super().__init__(**attrs)
        self.help = 'BLABLABLA'

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py') and filename != '__init__.py':
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        try:
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
        except FileNotFoundError:
            return
        return ns['cli']

    def run(self, name, ctx=None, **kwargs):
        if not ctx:
            ctx = click.get_current_context()
        cmd = self.get_command(ctx, name)

        if not cmd:
            return False  # @TODO raise instead ?
        return ctx.forward(cmd, **kwargs)

def load_modules(session):
    """ Load all modules """

    modules_paths = glob.glob(
        '%s/modules/*/[a-z]*py' % config.weevely_path
    )

    for module_path in modules_paths:

        module_group, module_filename = module_path.split(os.sep)[-2:]
        module_name = os.path.splitext(module_filename)[0]
        classname = module_name.capitalize()

        # Import module
        module = __import__(
            'modules.%s.%s' %
            (module_group, module_name), fromlist=["*"]
        )

        # Check if the module support folder exists
        folder = module_path.replace(
            module_filename,
            '_%s' % module_name
        )

        # Init class, passing current terminal instance and module
        # name
        module_class = getattr(module, classname)(
                        session,
                        '%s_%s' % (module_group, module_name),
                        folder
                       )

        loaded['%s_%s' %
            (module_group, module_name)] = module_class

        # Keep the tree in a dict of strings in the form
        # `{ 'group1' : [ 'mod1', 'mod2' ] }`
        tree_group = loaded_tree.get(module_group)
        if not tree_group:
            loaded_tree[module_group] = []
        loaded_tree[module_group].append('%s_%s' %
                            (module_group, module_name))
