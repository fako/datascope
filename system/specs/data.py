

class CommunityNumericCharacteristics(object):
    """
    Communities that benefit from structured content can use this class to put their content in a DataFrame
    Initializing should happen during "app ready" phase at Django startup
    The community should store the object in a cache
    When new partial content presents itself this can be passed into load_content
    When characteristics change load_characteristics can update all data for particular characteristics
    When all content or all characteristics updates this should get passed to reset with relevant parameter set
    """

    def __init__(self, identifier, content, characteristics):
        """
        Sets self.identifier for later use
        Calls reset with content and characteristics
        
        :param identifier: callable that takes content and returns the identifier
        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param characteristics: iterator with named callables that represent characteristics
        """
        pass

    def load_content(self, callable=None, characteristic_names=None):
        """
        Uses self.content if callable is set to None
        Uses self.characteristics.keys() if characteristic_names is None
        
        Calls callable which returns an iterator with content
        Passes each content to self.identifier to get content identity
        Get or creates row in self.data where identifier fills the index 
        and self.characteristics callables decide on values for columns
        Only fill columns defined by characteristic_names
        
        :param content: iterator with Individuals or content 
        :return: 
        """
        pass

    def load_characteristics(self, callables):
        """
        Takes the __name__ property from each callable and fills a dict self.characteristics where values are callables
        It adds __name__ as a column to self.data
        Calls load_content with characteristic_names set to names of callables
        
        :param callables: iterator with callables that return features 
        :return: 
        """
        pass

    def reset(self, content=None, characteristics=None):
        """
        Creates empty DataFrame in self.data
        Sets self.content to content if content is not None
        Sets self.characteristics to characteristics if characteristics is not None
        Calls load_characteristics if characteristics is set, otherwise calls load_content
        
        :param content: callable that returns lazy content iterator (e.g. lazy QuerySet iterator)
        :param characteristics: iterator with named callables that represent characteristics 
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
        Checks if keys in params exist in self.characteristics and if values are of correct type
        Should strip $ from start of keys
        
        :param params: dict of GET parameters
        :return: tuple with accepted and rejected items
        """
        pass
