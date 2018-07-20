import pandas as pd
import numpy as np


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

    def __init__(self, identifier, content, features):
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
        self.reset(content=content, features=features)

    def load_content(self, callable=None, feature_names=None):
        """
        Will call the callable to get the content.
        Then it will add the content to the DataFrame by calling all feature callables and add the return values.
        Specify feature_names to limit which feature callables will be used.
        Features not in this list will remain unchanged.
        
        :param content: iterator with Individuals or content
        :param feature_names: a list of feature names to load the content for
        :return: 
        """
        contents = callable() if callable else self.content()
        columns = feature_names if feature_names else self.features.keys()
        for content in contents:
            identifier = self.get_identifier(content)
            data = {}
            for column in columns:
                try:
                    value = self.features[column](content)
                except Exception as exc:
                    raise Exception("{} feature: {}".format(column, exc))
                try:
                    numeric = float(value)
                except ValueError:
                    raise ValueError("{} feature did not return float but {}".format(column, type(value)))
                data[column] = numeric
            series = pd.Series(data=data)
            try:
                row = self.data.loc[identifier].copy()
                row.update(series)
            except KeyError:
                row = series
            self.data.loc[identifier] = row

    def load_features(self, callables):
        """
        Will add all features in callables to the numeric frames as empty columns.
        As label it will use the name of the callable.
        Then it passes all content to load_content, but only loads content for the new features
        
        :param callables: iterator with callables that return features 
        :return: 
        """
        features = {
            callable.__name__: callable
            for callable in callables
        }
        self.features.update(features)
        feature_names = features.keys()
        for column in feature_names:
            self.data[column] = 0
        self.load_content(feature_names=feature_names)

    def reset(self, content=None, features=None):
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
        else:
            for column in self.features.keys():
                self.data[column] = 0
            self.load_content(content)

    def rank_by_params(self, params, limit=20):
        """
        Creates a Series out of params and then performs dotproduct on every row in DataFrame.
        It then sorts the scalars and returns indexes for highest scalars up to a amount of limit
        
        :param params: dict of GET parameters 
        :return: sorted list of index values
        """
        pass

    def clean_params(self, params):
        """
        Checks if keys in params exist in self.features and if values are of correct type
        Should strip $ from start of keys
        
        :param params: dict of GET parameters
        :return: tuple with accepted and rejected items
        """
        pass
