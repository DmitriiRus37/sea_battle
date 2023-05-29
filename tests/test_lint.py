import os
import unittest
import pycodestyle


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that the scripts conform to PEP-8."""
        style = pycodestyle.StyleGuide(ignore=['E501', 'E902'])
        files = set(os.listdir('..'))
        files_to_ignore = {'.git', 'venv', '.gitignore', 'README.md', 'requirements.py'}
        result = style.check_files(files - files_to_ignore)
        self.assertEqual(result.total_errors, 0)


