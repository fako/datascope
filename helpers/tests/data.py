from unittest import TestCase
from HIF.helpers.data import extractor


class TestPythonExtractor(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fixture_list = [
            1,
            2,
            3,
            "skip",
            "skip"
        ]
        cls.fixture_dict = {
            "include": "include",
            "skip": "skip",
            "include2": "include2"
        }
        cls.fixture_list_of_dicts = [
            cls.fixture_dict,
            cls.fixture_dict,
            cls.fixture_dict
        ]
        cls.fixture_dict_with_lists_of_dicts = {
            "list of dicts": cls.fixture_list_of_dicts,
            "skip": cls.fixture_list,
            "list of dicts 2": cls.fixture_list_of_dicts
        }
        cls.fixture_dict_with_dicts = {
            "dict": cls.fixture_dict,
            "skip": cls.fixture_list,
            "skip 2": "skip",
            "dict 2": cls.fixture_dict
        }

        cls.objective = {
            "include": None,
            "include2": None,
            "include3": True
        }

    def check_result(self, result):
        self.assertIsInstance(result, dict)
        self.assertIn("include", result)
        self.assertIn("include2", result)
        self.assertIn("include3", result)
        self.assertTrue(result["include3"])

    def test_dict(self):
        results = extractor(self.fixture_dict, self.objective)
        result = results[0]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.check_result(result)

    def test_list(self):
        results = extractor(self.fixture_list, self.objective)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_list_of_dicts(self):
        results = extractor(self.fixture_list_of_dicts, self.objective)
        result = results[0]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.check_result(result)

    def test_dict_with_lists_of_dicts(self):
        results = extractor(self.fixture_dict_with_lists_of_dicts, self.objective)
        result = results[0]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 6)
        self.check_result(result)

    def test_dict_with_dicts(self):
        results = extractor(self.fixture_dict_with_dicts, self.objective)
        result = results[0]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.check_result(result)