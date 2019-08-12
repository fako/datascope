import json
import hashlib

import pandas as pd
import numpy as np

from core.exceptions import DSFileLoadError
from json_field.fields import JSONEncoder


class NumericFeaturesFrame(object):
    """
    Communities that benefit from structured content can use this class to put their content in a DataFrame.
    The content gets transformed to floats for different purposes.
    Initializing should happen during "app ready" phase at Django startup
    The community should store the object in a cache
    When new partial content presents itself this can be passed into load_content
    When features change load_features can update all data for particular features
    When all content or all features update this should get passed to reset with relevant parameters set
    """

    def __init__(self, identifier, features, content=None, file_path=None):
        """
        Initiates a DataFrame and fills the frame using the content and features arguments.

        :param identifier: callable that takes content and returns the identifier
        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param features: iterator with named callables that represent features
        """
        self.get_identifier = identifier
        # Initialize attributes used by this class
        self.data = None
        self.content = None
        self.features = None
        # Fill actual data frame with content
        self.reset(features=features, content=content if not file_path else None)
        if file_path:
            self.from_disk(file_path)

    def from_disk(self, file_path):
        data = pd.read_pickle(file_path)
        columns_length = len(data.columns)
        features_length = len(self.features.keys())
        if columns_length != features_length:
            raise DSFileLoadError(
                "DataFrame loaded from disk columns count {} did not match features count {}".format(
                    columns_length, features_length
                )
            )
        for feature in self.features.keys():
            if feature not in data.columns:
                raise DSFileLoadError("{} feature not found in loaded DataFrame".format(feature))
        self.data = data

    def to_disk(self, file_path):
        self.data.to_pickle(file_path)

    def load_content(self, content_callable=None, feature_names=None):
        """
        Will call the callable to get the content.
        Then it will add the content to the DataFrame by calling all feature callables and add the return values.
        Specify feature_names to limit which feature callables will be used.
        Features not in this list will remain unchanged.

        :param content: iterator with Individuals or content
        :param feature_names: a list of feature names to load the content for
        :return:
        """
        columns = feature_names if feature_names else self.features.keys()
        assert len(columns), "Can't load_content if feature_names is an empty list or self.features is missing"

        new = pd.DataFrame()
        update = pd.DataFrame()
        for column in columns:
            series = self.get_feature_series(column, self.features[column], content_callable=content_callable)
            intersection = self.data[column].index.intersection(series.index)
            if len(intersection) == self.data.shape[0]:
                # the entire column is new
                # we simply add it to the frame
                self.data[column] = series
            else:
                # the column partially exists
                # we add what is new and update existing rows
                missing = series.index.difference(self.data[column].index)
                new[series.name] = series.loc[list(missing.get_values())]
                update[series.name] = series.loc[list(intersection.get_values())]
        self.data = self.data.append(new, sort=False)
        self.data.update(update)

    @staticmethod
    def get_content_hash(content):
        content_json = json.dumps(content, cls=JSONEncoder) if not hasattr(content, "properties") else \
            content.json_content
        hasher = hashlib.sha1()
        hasher.update(bytes(content_json, encoding="utf-8"))
        return hasher.digest()

    def get_feature_value(self, feature_name, feature_callable, content, content_hash, context=None):
        try:
            if context is None:
                value = feature_callable(content)
            else:
                value = feature_callable(content, context)
        except Exception as exc:
            raise Exception("{} feature: {}: {}".format(feature_name, exc.__class__.__name__, exc))
        try:
            numeric = float(value)
        except ValueError:
            raise ValueError("{} feature did not return float but {}".format(feature_name, type(value)))
        if self.get_content_hash(content) != content_hash:
            raise ValueError("{} feature modified content". format(feature_name))
        return numeric

    def get_feature_series(self, feature_name, feature_callable, content_callable=None, context=None):
        contents = content_callable() if content_callable else self.content()
        series = pd.Series(name=feature_name)
        for content in contents:
            content_hash = self.get_content_hash(content)
            identifier = self.get_identifier(content)
            series.at[identifier] = self.get_feature_value(feature_name, feature_callable, content, content_hash,
                                                           context)
        normalized = (series - series.min()) / (series.max() - series.min())
        return normalized.fillna(0)  # corrects divisions by 0

    def load_features(self, callables):
        """
        Will add all features in callables to the numeric frames as empty columns.
        As label it will use the name of the callable.
        Then it passes all content to load_content, but only loads content for the new features

        :param callables: iterator with callables that return features
        :return:
        """
        features = {
            feature_callable.__name__: feature_callable
            for feature_callable in callables
        }
        self.features.update(features)
        feature_names = features.keys()
        for column in feature_names:
            self.data[column] = pd.Series()
        if self.content is not None:
            self.load_content(feature_names=feature_names)

    def reset(self, features=None, content=None):
        """
        Either creates a DataFrame from scratch using content and features given.
        Or resets rows with only new content.
        Or resets columns with only new features.

        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param features: iterator with named callables that represent features
        :return:
        """
        assert content is not None or features is not None, \
            "Either content or features should be given to reset the numeric frame"
        self.data = pd.DataFrame(dtype=np.float)
        if content is not None:
            self.content = content
        if features is not None:
            self.features = {}
            self.load_features(features)
        elif self.features is not None and content is not None:
            for column in self.features.keys():
                self.data[column] = pd.Series()
            self.load_content(content)

    def rank_by_params(self, params, limit=20):
        """
        Creates a Series out of params and then performs dotproduct on every row in DataFrame.
        It then sorts the scalars and returns indexes for highest scalars up to a amount of limit

        :param params: dict of GET parameters
        :return: sorted list of index values
        """
        input_data = {key: 0.0 for key in self.features.keys()}
        input_data.update(self.clean_params(params))
        input_vector = pd.Series(data=input_data)
        ranking = self.data.dot(input_vector).sort_values(ascending=False)
        return list(ranking.index)

    def clean_params(self, params):
        """
        Checks if keys in params exist in self.features and if values are of correct type.
        Strip $ from start of keys.

        :param params: dict of GET parameters
        :return: tuple with accepted and rejected items
        """
        cleaned = {}
        for key, value in params.items():
            # First check valid values
            if isinstance(value, float):
                pass
            elif isinstance(value, int) or isinstance(value, str) and value.isnumeric():
                value = float(value)
            else:
                continue
            # Then check collisions and feature register
            stripped = key.strip("$")
            if stripped not in self.features:
                continue
            if stripped in cleaned:
                raise ValueError("Collision of keys while cleaning params for {} and {}".format(stripped, key))
            cleaned[stripped] = value
        return cleaned
