import sys
from unittest.mock import patch
import unittest
import shutil
import utils


class Test(unittest.TestCase):

    def test_check_available(self):
        with(
            patch('shutil.which', return_value="/usr/bin/python3"),
            patch('os.access', return_value=True)
        ):
            a = utils.check_available(["python3", "python3"])

            print(a)
