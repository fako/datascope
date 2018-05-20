import os
import shutil


class MissingFileSource(Exception):
    pass


class FileSorter(object):

    def __init__(self, source_base, destination_base):
        self.source_base = source_base
        self.destination_base = destination_base

    def __call__(self, files):
        for file_data in files:
            try:
                source_file_path = self.get_source(file_data)
            except MissingFileSource:
                continue
            source_file = os.path.join(self.source_base, source_file_path)
            destination_prefix = self.get_destination(file_data)
            destination = os.path.join(self.destination_base, destination_prefix)
            os.makedirs(destination, exist_ok=True)
            shutil.copy2(source_file, destination)

    def get_source(self, file_data):
        """
        Returns the source file name from file data

        :param file_data: various
        :return: (source_prefix, source_file_name,)
        """
        raise NotImplementedError()

    def get_destination(self, file_data):
        """
        Returns the destination prefix and file name from file data

        :param file_data: various
        :return: (destination_prefix, destination_file_name,)
        """
        raise NotImplementedError()
