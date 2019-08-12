from datetime import datetime, timedelta
from unittest import TestCase

from datagrowth.utils import parse_datetime_string, format_datetime, override_dict


class TestDatetimeUtils(TestCase):

    def test_parse_datetime_string(self):
        birth_day_text = "19850501071059010"
        birth_day_obj = datetime(year=1985, month=5, day=1, hour=7, minute=10, second=59)
        beginning_of_time = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
        parse = parse_datetime_string(birth_day_text)
        self.assertAlmostEqual(parse, birth_day_obj, delta=timedelta(seconds=1))
        birth_day_invalid = "01051985071059010"
        parse = parse_datetime_string(birth_day_invalid)
        self.assertEqual(parse, beginning_of_time)
        parse = parse_datetime_string(1534696182)
        self.assertEqual(parse, beginning_of_time)

    def test_format_datetime(self):
        birth_day_obj = datetime(year=1985, month=5, day=1, hour=7, minute=10, second=59)
        birth_day_text = format_datetime(birth_day_obj)
        self.assertEqual(birth_day_text, "19850501071059000000")
        try:
            format_datetime(1534696182)
            self.fail("format_datetime helper did not raise AttributeError when passing non-datetime")
        except AttributeError:
            pass


class TestIteratorUtils(TestCase):

    def test_ibatch(self):
        self.skipTest("not tested")


class TestOverrideDict(TestCase):

    def setUp(self):
        self.parent = {
            "test": "test",
            "test1": "parent"
        }
        self.child = {
            "test1": "child",
            "test2": "child2"
        }

    def test_override_dict(self):
        new_dict = override_dict(self.parent, self.child)
        self.assertEqual(new_dict, {"test": "test", "test1": "child", "test2": "child2"})
        new_dict = override_dict({}, self.child)
        self.assertEqual(new_dict, self.child)
        new_dict = override_dict(self.parent, {})
        self.assertEqual(new_dict, self.parent)

    def test_invalid_input(self):
        try:
            override_dict(self.parent, "child")
            self.fail("override_dict did not fail when receiving other type than dict as child")
        except AssertionError:
            pass
        try:
            override_dict(["parent"], self.child)
            self.fail("override_dict did not fail when receiving other type than dict as parent")
        except AssertionError:
            pass

    def test_override_dict_deep(self):
        self.parent["deep"] = {
            "constant": True,
            "variable": False
        }
        self.child["deep"] = {
            "variable": True
        }
        new_dict = override_dict(self.parent, self.child)
        self.assertEqual(new_dict, {
            "test": "test",
            "test1": "child",
            "test2": "child2",
            "deep": {
                # NB: deletes the constant key from parent!!
                "variable": True
            }
        })
