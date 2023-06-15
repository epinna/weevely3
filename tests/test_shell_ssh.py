from core import modules
from core.sessions import SessionURL
from tests.base_test import BaseTest
from tests.config import su_user, su_passwd


class ShellSsh(BaseTest):
    def setUp(self):
        self.session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(self.session)

        self.vector_list = modules.loaded['shell_ssh'].vectors.get_names()
        self.run_argv = modules.loaded['shell_ssh'].run_argv

    def test_param_vector(self):
        for vect in self.vector_list:
            output = self.run_argv(['-vector', vect, f'{su_user}@localhost', su_passwd, 'whoami'])
            self.assertEqual(output.rstrip(), su_user)
