class OrganismInputProtocol(object):
    """
    Anything that acts as input for Organisms should implement this protocol.
    """

    @property
    def input_for_organism(self):
        """
        This method should return the occasion (spirit) to get the data. The type of the data and the data itself.
        This way an Organism can read the data and other processes can query on the Organism.spirit.

        :return: spirit, content_type, data
        """
        return None, None, None