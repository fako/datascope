import pandas as pd


class NumericFeaturesFrame(object):
    """
    Communities that benefit from structured content can use this class to put their content in a DataFrame
    Initializing should happen during "app ready" phase at Django startup
    The community should store the object in a cache
    When new partial content presents itself this can be passed into load_content
    When features change load_features can update all data for particular features
    When all content or all features update this should get passed to reset with relevant parameters set
    """

    def __init__(self, identifier, content, features):
        """
        Sets self.identifier for later use
        Calls reset with content and features
        
        :param identifier: callable that takes content and returns the identifier
        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param features: iterator with named callables that represent features
        """
        pass

    def load_content(self, callable=None, feature_names=None):
        """
        Uses self.content if callable is set to None
        Uses self.features.keys() if feature_names is None
        
        Calls callable which returns an iterator with content
        Passes each content to self.identifier to get content identity
        Get or creates row in self.data where identifier fills the index 
        and self.features callables decide on values for columns
        Only fill columns defined by feature_names
        
        :param content: iterator with Individuals or content 
        :return: 
        """
        pass

    def load_features(self, callables):
        """
        Takes the __name__ property from each callable and fills a dict self.features where values are callables
        It adds __name__ as a column to self.data
        Calls load_content with feature_names set to names of callables
        
        :param callables: iterator with callables that return features 
        :return: 
        """
        pass

    def reset(self, content=None, features=None):
        """
        Creates empty DataFrame in self.data
        Sets self.content to content if content is not None
        Sets self.features to features if features is not None
        Calls load_features if features is set, otherwise calls load_content
        
        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param features: iterator with named callables that represent features
        :return: 
        """
        pass

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
