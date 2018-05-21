import os
import shutil
from random import shuffle
from glob import glob
from collections import Counter


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


class FileBalancer(object):

    def __init__(self, train_files, validate_files, test_files, dry_run=True):
        self.train_files = train_files
        self.validate_files = validate_files
        self.test_files = test_files
        self.dry_run = dry_run

    def __call__(self, target):
        for category_path in glob(target + "/train/*/"):
            category = self.get_category(category_path)
            imbalance = self.balance_category(target, category)
            if imbalance < 0:
                print("upsampled", category, abs(imbalance))

    def get_category(self, path):
        path_segments = path.split("/")
        return path_segments[-2]

    def get_data_type(self, path):
        path_segments = path.split("/")
        return path_segments[-3]

    def random_move(self, source, target, count):
        source_paths = glob(source)
        shuffle(source_paths)
        for source_path in source_paths[:count]:
            if self.dry_run:
                print("Moving {} to {}".format(source_path, target))
            else:
                tail, head = os.path.split(source_path)
                os.replace(source_path, os.path.join(target, head))

    def random_upsample(self, source, count):
        source_paths = glob(source)
        shuffle(source_paths)
        for ix, source_path in enumerate(source_paths[:count]):
            head, tail = os.path.split(source_path)
            target_path = "{}/{}_{}".format(head, ix, tail)
            if self.dry_run:
                print("Up sampling {} to {}".format(source_path, target_path))
            else:
                shutil.copy2(source_path, target_path)

    def random_remove(self, source, count):
        source_paths = glob(source)
        shuffle(source_paths)
        for source_path in source_paths[:count]:
            if self.dry_run:
                print("Removing {}".format(source_path))
            else:
                os.remove(source_path)

    def balance_category(self, target, category):
        type_counter = Counter([
            self.get_data_type(path)
            for path in glob(target + "/*/{}/*.*".format(category))
        ])
        test_imbalance = type_counter["test"] - self.test_files
        if test_imbalance < 0:
            file_shortage = abs(test_imbalance)
            self.random_move(
                "{}/train/{}/*.*".format(target, category),
                "{}/test/{}/".format(target, category),
                file_shortage
            )
            type_counter["test"] += file_shortage
            type_counter["train"] -= file_shortage
        elif test_imbalance > 0:
            file_surplus = test_imbalance
            self.random_move(
                "{}/test/{}/*.*".format(target, category),
                "{}/train/{}/".format(target, category),
                file_surplus
            )
            type_counter["test"] -= file_surplus
            type_counter["train"] += file_surplus
        valid_imbalance = type_counter["valid"] - self.validate_files
        if valid_imbalance < 0:
            file_shortage = abs(valid_imbalance)
            self.random_move(
                "{}/train/{}/*.*".format(target, category),
                "{}/valid/{}/".format(target, category),
                file_shortage
            )
            type_counter["valid"] += file_shortage
            type_counter["train"] -= file_shortage
        elif valid_imbalance > 0:
            file_surplus = valid_imbalance
            self.random_move(
                "{}/valid/{}/*.*".format(target, category),
                "{}/train/{}/".format(target, category),
                file_surplus
            )
            type_counter["valid"] -= file_surplus
            type_counter["train"] += file_surplus
        train_imbalance = type_counter["train"] - self.train_files
        if train_imbalance < 0:
            self.random_upsample(
                "{}/train/{}/*.*".format(target, category),
                abs(train_imbalance)
            )
        elif train_imbalance > 0:
            self.random_remove(
                "{}/train/{}/*.*".format(target, category),
                train_imbalance
            )
        return train_imbalance
