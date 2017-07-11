from tests.base_test import BaseTest
from core.weexceptions import ArgparseError
from core.vectors import PhpCode
from core.vectors import Os
from core import modules
from core.sessions import SessionURL
from core import messages
from tests.config import su_user, su_passwd
import core.config
import unittest
import logging
import os

class ShellSu(BaseTest):

    def setUp(self):
        self.session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(self.session)

        self.vector_list = modules.loaded['shell_su'].vectors.get_names()

        self.run_argv = modules.loaded['shell_su'].run_argv


    def test_param_vector(self):

        for vect in self.vector_list:
            # Check correctness of execution
            self.assertEqual(self.run_argv(["-vector", vect, "-u", su_user, su_passwd, "whoami"]).rstrip(), su_user);
            