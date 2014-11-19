from unittest import TestCase
from core.helpers.data import extractor, reach, expand, interpolate


class TestPythonReach(TestCase):

    def setUp(self):
        self.test_dict = {
            "dict": {
                "test": "nested value",
                "list": ["nested value 0", "nested value 1", "nested value 2"],
                "dict": {"test": "test"}
            },
            "list": ["value 0", "value 1", "value 2"],
            "dotted.key": "another value"
        }
        self.test_list = [
            {"test": "dict in list"}
        ]

    def test_dict_access(self):
        self.assertEqual(reach("dict.test", self.test_dict), self.test_dict["dict"]["test"])
        self.assertEqual(reach("dict.dict", self.test_dict), self.test_dict["dict"]["dict"])
        self.assertEqual(reach("dict.list", self.test_dict), self.test_dict["dict"]["list"])

    def test_list_access(self):
        self.assertEqual(reach("list.0", self.test_dict), self.test_dict["list"][0])
        self.assertEqual(reach("dict.list.0", self.test_dict), self.test_dict["dict"]["list"][0])
        self.assertEqual(reach("0.test", self.test_list), self.test_list[0]["test"])

    def test_key_with_dots(self):
        self.assertEqual(reach("dotted.key", self.test_dict), self.test_dict["dotted.key"])

    def test_invalid_key(self):
        self.assertEqual(reach("does.not.exist", self.test_dict), None)

    def test_none_key(self):
        self.assertEqual(reach(None, self.test_dict), self.test_dict)
        self.assertEqual(reach(None, self.test_list), self.test_list)

    def test_invalid_data(self):
        try:
            reach("irrelevant", "invalid-input")
            self.fail("Reach did not throw a TypeError after getting invalid input")
        except TypeError as exception:
            self.assertEqual(str(exception), "Reach needs dict as input, got <type 'str'> instead")


class TestPythonExtractor(TestCase):

    def setUp(self):
        self.fixture_list = [
            1,
            2,
            3,
            "skip",
            "skip"
        ]
        self.fixture_dict = {
            "include": "include",
            "skip": "skip",
            "include2": "include2"
        }
        self.fixture_list_of_dicts = [
            self.fixture_dict,
            self.fixture_dict,
            self.fixture_dict
        ]
        self.fixture_dict_with_lists_of_dicts = {
            "list of dicts": self.fixture_list_of_dicts,
            "skip": self.fixture_list,
            "list of dicts 2": self.fixture_list_of_dicts
        }
        self.fixture_dict_with_dicts = {
            "dict 1": self.fixture_dict,
            "skip": self.fixture_list,
            "skip 2": "skip",
            "dict 2": self.fixture_dict
        }
        self.fixture_reach = {
            "dict": {
                "dict": True
            },
            "list": [False, False, True]
        }

        self.objective = {
            "include": None,
            "include2": None,
            "include3": True,
            "dict.dict": None,
            "list.2": None
        }

    def check_result(self, result):
        self.assertIsInstance(result, dict)
        self.assertIn("include", result)
        self.assertIn("include2", result)
        self.assertIn("include3", result)
        self.assertIn("dict.dict", result)
        self.assertIn("list.2", result)
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

    def test_reach(self):
        # check reach results
        results = extractor(self.fixture_reach, self.objective)
        result = results[0]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.check_result(result)
        self.assertTrue(result["dict.dict"])
        self.assertTrue(result["list.2"])
        # invalid triggers shouldn't create any objects
        self.fixture_reach["dict"] = False
        self.fixture_reach["list"] = False
        results = extractor(self.fixture_reach, self.objective)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)


class TestPythonExpand(TestCase):

    def setUp(self):
        self.test_dict = {
            "dict": {
                "test": "nested value",
                "list": ["nested value 0", "nested value 1", "nested value 2"],
                "dict": {"test": "test"}
            },
            "list": ["value 0", "value 1", "value 2"],
            "dotted.key": "another value"
        }
        self.test_list = [
            self.test_dict, self.test_dict, self.test_dict
        ]

    def test_list_in_dict(self):
        results = expand('list.*', self.test_dict)
        self.assertEqual(results, ['list.0', 'list.1', 'list.2'])

    def test_list(self):
        results = expand('*', self.test_list)
        self.assertEqual(results, ['0', '1', '2'])

    def test_list_of_dicts(self):
        results = expand('*.dict', self.test_list)
        self.assertEqual(results, ['0.dict', '1.dict', '2.dict'])

    def test_list_of_dicts_with_list(self):
        results = expand('*.dict.list.*', self.test_list)
        self.assertEqual(results, [
            '0.dict.list.0', '0.dict.list.1', '0.dict.list.2',
            '1.dict.list.0', '1.dict.list.1', '1.dict.list.2',
            '2.dict.list.0', '2.dict.list.1', '2.dict.list.2',
        ])


class TestPythonInterpolate(TestCase):

    def test_single_interpolation(self):
        result = interpolate('*', '8')
        self.assertEqual(result, '8')

    def test_multi_interpolation(self):
        result = interpolate('*.this.is.*.simply.*.test', '6.this.is.3.simply.1.test')
        self.assertEqual(result, '6.this.is.3.simply.1.test')

    def test_shorter_source(self):
        result = interpolate('*.this.is.*.simply.a.test', '6.this.is.3')
        self.assertEqual(result, '6.this.is.3.simply.a.test')

    def test_longer_source(self):
        result = interpolate('*.this.is.*.simply.a.test', '6.this.is.3.simply.a.test.8.5.longer.3.is.ignored')
        self.assertEqual(result, '6.this.is.3.simply.a.test')

    def test_mismatch_paths(self):
        try:
            interpolate('*.this.is.*.simply.a.test', '6.this.is.666.not.correct')
        except ValueError as exception:
            self.assertEqual(
                str(exception),
                "Can't interpolate *.this.is.*.simply.a.test with 6.this.is.666.not.correct, because paths differ at simply/not."
            )
            return
        self.fail("Did not raise ValueError on path mismatch.")

    def test_non_digit(self):
        try:
            interpolate('*.this.is.*.simply.a.test', '6.this.is.not.correct')
        except ValueError as exception:
            self.assertEqual(str(exception), "Can't interpolate * with non-digit value 'not'.")
            return
        self.fail("Did not raise ValueError on path mismatch.")