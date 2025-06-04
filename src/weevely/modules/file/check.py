import datetime

from weevely import utils
from weevely.core.module import Module
from weevely.core.vectors import PhpCode


class Check(Module):
    """Get attributes and permissions of a file."""

    def init(self):
        self.register_info({"author": ["Emilio Pinna"], "license": "GPLv3"})

        # Declared here since is used by multiple vectors
        payload_perms = (
            "$f='${rpath}';if(@file_exists($f)){print('e');if(@is_readable($f))print('r');"
            "if(@is_writable($f))print('w');if(@is_executable($f))print('x');}"
            "$f='${rpath}';if(@file_exists($f)){print('e');if(@is_readable($f))print('r');"
            "if(@is_writable($f))print('w');if(@is_executable($f))print('x');}"
        )

        self.register_vectors(
            [
                PhpCode(payload_perms, "exists", postprocess=lambda x: "e" in x),
                PhpCode("print(md5_file('${rpath}'));", "md5"),
                PhpCode(payload_perms, "perms"),
                PhpCode(payload_perms, "readable", postprocess=lambda x: "r" in x),
                PhpCode(payload_perms, "writable", postprocess=lambda x: "w" in x),
                PhpCode(payload_perms, "executable", postprocess=lambda x: "x" in x),
                PhpCode("print(is_file('${rpath}') ? 1 : 0);", "file", postprocess=lambda x: x == "1"),
                PhpCode("print(is_dir('${rpath}') ? 1 : 0);", "dir", postprocess=lambda x: x == "1"),
                PhpCode(
                    "print(filesize('${rpath}'));", "size", postprocess=lambda x: utils.prettify.format_size(int(x))
                ),
                PhpCode("print(filemtime('${rpath}'));", "time", postprocess=lambda x: int(x)),
                PhpCode(
                    "print(filemtime('${rpath}'));",
                    "datetime",
                    postprocess=lambda x: datetime.datetime.fromtimestamp(float(x)).strftime("%Y-%m-%d %H:%M:%S"),
                ),
                PhpCode("print(realpath('${rpath}'));", "abspath"),
            ]
        )

        self.register_arguments(
            [
                {"name": "rpath", "help": "Target path"},
                {"name": "check", "choices": self.vectors.get_names()},
            ]
        )

    def run(self, **kwargs):
        return self.vectors.get_result(name=self.args["check"], format_args=self.args)
