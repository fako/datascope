from unittest.mock import patch, Mock

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from django.test import TestCase

from core.utils.data import NumericFeaturesFrame
from core.models import Collective, Individual
from core.exceptions import DSFileLoadError


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
        test_frame = pd.DataFrame.from_records(self.test_records, index=[4, 5, 6, 7, 8])
        test_frame = (test_frame - test_frame.min()) / (test_frame.max() - test_frame.min())
        self.test_frame = test_frame.fillna(0)
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
        test_frame_extra = pd.DataFrame.from_records(self.test_records + self.test_records_extra,
                                                          index=[4, 5, 6, 7, 8, 9, 10])
        test_frame_extra = (test_frame_extra - test_frame_extra.min()) / \
                           (test_frame_extra.max() - test_frame_extra.min())
        self.test_frame_extra = test_frame_extra.fillna(0)
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
        self.extra_individuals = [
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
        ]

    @staticmethod
    def get_identifier(test):
        return test.id

    def get_iterator(self):
        """
        Returns content that is already in fixtures
        """
        return self.test_fixture.individual_set.filter(id__lt=9).iterator()

    def get_extra_iterator(self):
        """
        Returns content that is created in setUp
        """
        return iter(self.extra_individuals)

    @staticmethod
    def is_dutch(test):
        return float(test["language"] == "nl")

    @staticmethod
    def is_english(test):
        return int(test["language"] == "en")  # NB: features should return floats, but ints are allowed

    @staticmethod
    def value_number(test):
        return test["value"]

    @staticmethod
    def invalid_arguments():
        return 0.0

    @staticmethod
    def invalid_return(test):
        return "invalid"

    @staticmethod
    def set_language_to_fr(test):
        test["language"] = "fr"
        return 0.0

    def test_init(self):
        sorted_feature_names = ["is_dutch", "is_english", "value_number"]
        self.assertEqual(
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

    def test_init_immutable_content(self):
        content = list(self.get_iterator())
        features = [
            TestNumericFeaturesFrame.set_language_to_fr
        ]
        try:
            NumericFeaturesFrame(
                self.get_identifier,
                features,
                lambda: content
            )
            self.fail("NumericFeaturesFrame did not raise when features modified content")
        except ValueError:
            pass

    def test_init_file(self):
        with patch("core.utils.data.numeric_features.NumericFeaturesFrame.from_disk", return_value=self.test_frame) as \
                from_disk_patch:
            frame = NumericFeaturesFrame(
                self.get_identifier,
                self.features,
                file_path="test/path/to/frame.pkl"
            )
            sorted_feature_names = ["is_dutch", "is_english", "value_number"]
            self.assertEqual(
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

    def test_from_disk_invalid(self):
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
        self.assertEqual(
            sorted(self.frame.features.keys()),
            sorted_feature_names
        )

    def test_adding_content(self):
        self.frame.load_content(self.get_extra_iterator)
        assert_frame_equal(self.frame.data, self.test_frame_extra, check_like=True)

    def test_adding_content_mixed(self):
        self.skipTest("Bug: GH-109")
        old = list(self.get_iterator())[-2:]

        def update(ind):
            ind.properties["value"] = int(ind.properties["value"]) * 5
            return ind

        updated = list(map(update, old))
        self.frame.load_content(
            lambda: iter(list(self.get_extra_iterator()) + updated)
        )
        self.test_frame_extra["value_number"].loc[[7, 8]] *= 5
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
        self.assertEqual(
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
        self.assertEqual(
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
        self.assertEqual(
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
            self.assertEqual(cleaned_params, {"is_dutch": 1.0, "value_number": 2.0})

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
        self.assertEqual(ranking, [5, 8, 6, 4, 7])
        ranking = self.frame.rank_by_params({"is_dutch": 0.5, "value_number": -1, "is_english": 2, "is_french": 100})
        self.assertEqual(ranking, [7, 8, 6, 4, 5])

    def test_get_content_hash(self):
        self.skipTest("not tested")

    def test_get_feature_value(self):
        self.skipTest("not tested")

    def test_get_feature_series(self):
        self.skipTest("not tested")
