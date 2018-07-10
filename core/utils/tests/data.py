import pandas as pd
from pandas.testing import assert_frame_equal

from django.test import TestCase

from core.utils.data import reach, NumericFeaturesFrame
from core.models import Collective


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
        except TypeError:
            pass


class TestNumericFeaturesFrame(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super().setUp()
        self.test_fixture = Collective.objects.get(id=2)
        self.test_records = [
            {
                "is_dutch": 1.0,
                "is_english": 0.0,
                "value_number": 1.0
            },
            {
                "is_dutch": 1.0,
                "is_english": 0.0,
                "value_number": 2.0
            },
            {
                "is_dutch": 1.0,
                "is_english": 0.0,
                "value_number": 1.0
            },
            {
                "is_dutch": 0.0,
                "is_english": 1.0,
                "value_number": 1.0
            },
            {
                "is_dutch": 0.0,
                "is_english": 1.0,
                "value_number": 2.0
            }
        ]
        self.test_frame = pd.DataFrame.from_records(self.test_records, index=[4,5,6,7,8])

    @staticmethod
    def get_identifier(test):
        return test.id

    def get_iterator(self):
        return self.test_fixture.individual_set.iterator()

    @staticmethod
    def is_dutch(test):
        return int(test.properties["language"] == "nl")

    @staticmethod
    def is_english(test):
        return int(test.properties["language"] == "en")

    @staticmethod
    def value_number(test):
        return test.properties["value"]

    def test_init(self):
        features = [
            TestNumericFeaturesFrame.is_dutch,
            TestNumericFeaturesFrame.is_english,
            TestNumericFeaturesFrame.value_number
        ]
        frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            self.get_iterator,
            features
        )
        sorted_feature_names = ["is_dutch", "is_english", "value_number"]
        self.assertEquals(
            sorted(frame.features.keys()),
            sorted_feature_names
        )
        self.assertTrue(callable(frame.content))
        assert_frame_equal(frame.data, self.test_frame, check_like=True)
