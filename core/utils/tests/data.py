from mock import patch, Mock

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from django.test import TestCase

from core.utils.data import reach, NumericFeaturesFrame
from core.models import Collective, Individual
from core.exceptions import DSFileLoadError


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
        self.test_frame = pd.DataFrame.from_records(self.test_records, index=[4, 5, 6, 7, 8])
        self.test_records_extra = [
            {
                "is_dutch": 0.0,
                "is_english": 0.0,
                "value_number": 1.0
            },
            {
                "is_dutch": 0.0,
                "is_english": 0.0,
                "value_number": 2.0
            }
        ]
        self.test_frame_extra = pd.DataFrame.from_records(self.test_records + self.test_records_extra,
                                                          index=[4, 5, 6, 7, 8, 9, 10])
        self.features = [
            TestNumericFeaturesFrame.is_dutch,
            TestNumericFeaturesFrame.is_english,
            TestNumericFeaturesFrame.value_number
        ]
        self.frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            self.features,
            self.get_iterator
        )

    @staticmethod
    def get_identifier(test):
        return test.id

    def get_iterator(self):
        return self.test_fixture.individual_set.iterator()

    def get_extra_iterator(self):
        return iter([
            Individual.objects.create(
                id=9,
                properties={
                    'country': 'FR',
                    'language': 'fr',
                    'value': '1',
                    'word': 'pension'
                },
                community=self.test_fixture.community,
                collective=self.test_fixture
            ),
            Individual.objects.create(
                id=10,
                properties={
                    'country': 'FR',
                    'language': 'fr',
                    'value': '2',
                    'word': 'pension'
                },
                community=self.test_fixture.community,
                collective=self.test_fixture
            )
        ])

    @staticmethod
    def is_dutch(test):
        return int(test.properties["language"] == "nl")

    @staticmethod
    def is_english(test):
        return int(test.properties["language"] == "en")

    @staticmethod
    def value_number(test):
        return test.properties["value"]

    @staticmethod
    def invalid_arguments():
        return 0.0

    @staticmethod
    def invalid_return(test):
        return "invalid"

    def test_init(self):
        sorted_feature_names = ["is_dutch", "is_english", "value_number"]
        self.assertEquals(
            sorted(self.frame.features.keys()),
            sorted_feature_names
        )
        self.assertTrue(callable(self.frame.content))
        assert_frame_equal(self.frame.data, self.test_frame, check_like=True)

    def test_init_invalid_features(self):
        features = [
            TestNumericFeaturesFrame.invalid_arguments
        ]
        try:
            NumericFeaturesFrame(
                TestNumericFeaturesFrame.get_identifier,
                features,
                self.get_iterator
            )
            self.fail("NumericFeaturesFrame did not raise with invalid feature")
        except Exception as exc:
            self.assertEqual(
                str(exc),
                "invalid_arguments feature: TypeError: invalid_arguments() takes 0 positional arguments but 1 was given"
            )
        features = [
            TestNumericFeaturesFrame.invalid_return
        ]
        try:
            NumericFeaturesFrame(
                TestNumericFeaturesFrame.get_identifier,
                features,
                self.get_iterator
            )
            self.fail("NumericFeaturesFrame did not raise with invalid feature return value")
        except ValueError as exc:
            self.assertEqual(
                str(exc),
                "invalid_return feature did not return float but <class 'str'>"
            )

    def test_init_file(self):
        with patch("core.utils.data.numeric_features.NumericFeaturesFrame.from_disk", return_value=self.test_frame) as \
                from_disk_patch:
            frame = NumericFeaturesFrame(
                self.get_identifier,
                self.features,
                file_path="test/path/to/frame.pkl"
            )
            sorted_feature_names = ["is_dutch", "is_english", "value_number"]
            self.assertEquals(
                sorted(frame.features.keys()),
                sorted_feature_names
            )
            from_disk_patch.assert_called_once_with("test/path/to/frame.pkl")

    def test_to_disk(self):
        self.frame.data.to_pickle = Mock()
        self.frame.to_disk("test/path/to/frame.pkl")
        self.frame.data.to_pickle.assert_called_once_with('test/path/to/frame.pkl')

    def test_from_disk(self):
        with patch("core.utils.data.numeric_features.pd.read_pickle", return_value=self.test_frame) as pandas_patch:
            self.frame.from_disk("test/path/to/frame.pkl")
            pandas_patch.assert_called_once_with("test/path/to/frame.pkl")
            assert_frame_equal(self.frame.data, self.test_frame, check_like=True)

    def test_init_file_invalid(self):
        self.test_frame["extra"] = self.test_frame["is_dutch"]
        with patch("core.utils.data.numeric_features.pd.read_pickle", return_value=self.test_frame) as pandas_patch:
            try:
                self.frame.from_disk("test/path/to/frame.pkl")
                self.fail("NumericFeatureFrame.from_disk did not raise an assertion when loading too much data")
            except DSFileLoadError as exc:
                pass
            pandas_patch.assert_called_once_with("test/path/to/frame.pkl")
        self.test_frame.drop("is_dutch", axis=1)
        with patch("core.utils.data.numeric_features.pd.read_pickle", return_value=self.test_frame) as pandas_patch:
            try:
                self.frame.from_disk("test/path/to/frame.pkl")
                self.fail("NumericFeatureFrame.from_disk did not raise an assertion when loading wrong data")
            except DSFileLoadError:
                pass
            pandas_patch.assert_called_once_with("test/path/to/frame.pkl")
        self.test_frame.drop("extra", axis=1)
        with patch("core.utils.data.numeric_features.pd.read_pickle", return_value=self.test_frame) as pandas_patch:
            try:
                self.frame.from_disk("test/path/to/frame.pkl")
                self.fail("NumericFeatureFrame.from_disk did not raise an assertion when loading too little data")
            except DSFileLoadError:
                pass
            pandas_patch.assert_called_once_with("test/path/to/frame.pkl")

    def test_adding_features(self):
        features = [
            TestNumericFeaturesFrame.is_dutch
        ]
        frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            features,
            self.get_iterator
        )
        frame.load_features([
            TestNumericFeaturesFrame.value_number,
            TestNumericFeaturesFrame.is_english
        ])
        assert_frame_equal(frame.data, self.test_frame, check_like=True)
        sorted_feature_names = ["is_dutch", "is_english", "value_number"]
        self.assertEquals(
            sorted(self.frame.features.keys()),
            sorted_feature_names
        )

    def test_adding_content(self):
        self.frame.load_content(self.get_extra_iterator)
        assert_frame_equal(self.frame.data, self.test_frame_extra, check_like=True)

    def test_resetting_features_and_content(self):
        features = [
            TestNumericFeaturesFrame.is_dutch
        ]
        frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            features,
            self.get_iterator
        )
        frame.reset(
            features=[
                TestNumericFeaturesFrame.value_number,
                TestNumericFeaturesFrame.is_english
            ],
            content=self.get_extra_iterator
        )
        self.test_frame_extra = self.test_frame_extra.drop([4, 5, 6, 7, 8], axis=0)
        self.test_frame_extra = self.test_frame_extra.drop(labels="is_dutch", axis=1)
        assert_frame_equal(frame.data, self.test_frame_extra, check_like=True)
        sorted_feature_names = ["is_english", "value_number"]
        self.assertEquals(
            sorted(frame.features.keys()),
            sorted_feature_names
        )

    def test_resetting_features(self):
        features = [
            TestNumericFeaturesFrame.is_dutch
        ]
        frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            features,
            self.get_iterator
        )
        frame.reset(features=[
            TestNumericFeaturesFrame.value_number,
            TestNumericFeaturesFrame.is_english
        ])
        self.test_frame = self.test_frame.drop(labels="is_dutch", axis=1)
        assert_frame_equal(frame.data, self.test_frame, check_like=True)
        sorted_feature_names = ["is_english", "value_number"]
        self.assertEquals(
            sorted(frame.features.keys()),
            sorted_feature_names
        )

    def test_resetting_features_no_content(self):
        features = [
            TestNumericFeaturesFrame.is_dutch
        ]
        frame = NumericFeaturesFrame(
            TestNumericFeaturesFrame.get_identifier,
            features
        )
        frame.reset(features=[
            TestNumericFeaturesFrame.value_number,
            TestNumericFeaturesFrame.is_english
        ])
        self.test_frame = self.test_frame.drop(labels="is_dutch", axis=1)
        assert_frame_equal(frame.data, self.test_frame[0:0], check_like=True)
        sorted_feature_names = ["is_english", "value_number"]
        self.assertEquals(
            sorted(frame.features.keys()),
            sorted_feature_names
        )

    def test_resetting_content(self):
        self.frame.reset(content=self.get_extra_iterator)
        self.test_frame_extra = self.test_frame_extra.drop([4, 5, 6, 7, 8], axis=0)
        assert_frame_equal(self.frame.data, self.test_frame_extra, check_like=True)

    def test_resetting_content_no_features(self):
        self.frame.features = None
        self.frame.reset(content=self.get_extra_iterator)
        self.assertEqual(self.frame.content.__name__, self.get_extra_iterator.__name__)  # TODO: better equality test
        assert_frame_equal(self.frame.data, pd.DataFrame(dtype=np.float), check_like=True)

    def test_clean_params(self):
        test_params = {
            "is_dutch": "1",  # get converted to float
            "is_french": 1.0,  # gets skipped
            "$is_french": 1.0,  # gets skipped (without errors)
            "value_number": None,  # gets skipped a a non-numeric
            "is_english": "test",  # gets skipped as a non-numeric
            "$value_number": 2.0
        }
        for function in [str, int, float]:
            test_params["is_dutch"] = function(test_params["is_dutch"])
            cleaned_params = self.frame.clean_params(test_params)
            self.assertEquals(cleaned_params, {"is_dutch": 1.0, "value_number": 2.0})

        test_error_params = {
            "is_dutch": "1",
            "$is_dutch": 1.0,
        }
        try:
            self.frame.clean_params(test_error_params)
            self.fail("Clean params should have raised for invalid params")
        except ValueError:
            pass

    def test_rank_by_params(self):
        ranking = self.frame.rank_by_params({"is_dutch": 1, "value_number": 1})
        self.assertEquals(ranking, [5, 8, 6, 4, 7])
        ranking = self.frame.rank_by_params({"is_dutch": 0.5, "value_number": -1, "is_english": 2, "is_french": 100})
        self.assertEquals(ranking, [7, 8, 6, 4, 5])
