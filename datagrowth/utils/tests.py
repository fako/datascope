from datetime import datetime, timedelta
from unittest import TestCase

from datagrowth.utils import parse_datetime_string, format_datetime


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
