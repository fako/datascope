import os
import pickle

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer


class TextContentReader(object):

    def __init__(self, get_identifier, content_callable):
        self.get_identifier = get_identifier
        self.content_callable = content_callable
        self.content = None
        self.identifiers = None

    def __iter__(self):
        self.content = self.content_callable()
        self.identifiers = []
        return self

    def __next__(self):
        entry = next(self.content)
        self.identifiers.append(self.get_identifier(entry))
        return entry


class TextFeaturesFrame(object):

    def __init__(self, identifier, content=None, file_path=None):
        assert content is not None or file_path is not None, \
            "Either content or file_path should be given to init a TextFeaturesFrame"
        self.get_identifier = identifier
        # Initialize attributes used by this class
        self.raw_data = None
        self.vectorizer = None
        self.data = None
        self.content = None
        self.features = None
        self.count_dtype = np.int16
        # Fill actual data frame with content
        if file_path:
            self.from_disk(file_path)
        else:
            self.reset(content=content)

    def from_disk(self, file_path):
        file_name, ext = os.path.splitext(file_path)
        self.raw_data = pd.read_pickle(file_path)
        with open(file_name + ".voc", "rb") as vocab_file:
            self.vectorizer = pickle.load(vocab_file)
        self.load_features(self.vectorizer)
        self.load_data(self.raw_data)

    def to_disk(self, file_path):
        file_name, ext = os.path.splitext(file_path)
        self.raw_data.to_pickle(file_path)
        with open(file_name + ".voc", "wb") as vocab_file:
            pickle.dump(self.vectorizer, vocab_file)

    def get_vectorizer(self):
        return CountVectorizer()

    def load_data(self, raw_data):
        transformer = TfidfTransformer()
        tfidf_matrix = transformer.fit_transform(raw_data.to_coo())
        self.data = pd.SparseDataFrame(tfidf_matrix)
        self.data /= self.data.max().max()  # min-max normalisation across columns with min=0

    def load_content(self, content_callable=None):
        if not self.vectorizer:
            self.vectorizer = self.get_vectorizer()
            should_fit = True
        else:
            should_fit = False
        content_reader = TextContentReader(self.get_identifier, content_callable or self.content)
        # Get vector and identifier for batch
        matrix = self.vectorizer.fit_transform(content_reader) if should_fit \
            else self.vectorizer.transform(content_reader)
        frame = pd.SparseDataFrame(matrix, index=content_reader.identifiers, dtype=self.count_dtype)
        # Update existing data and deduplicate on index
        self.raw_data = pd.concat([self.raw_data, frame])
        duplicates = self.raw_data.index.duplicated(keep="first")
        if duplicates.any():
            self.raw_data = self.raw_data[~duplicates]
        self.load_data(self.raw_data)
        if should_fit:
            self.load_features(self.vectorizer)

    def load_features(self, vectorizer):
        self.features = {
            feature: ix
            for ix, feature in enumerate(vectorizer.get_feature_names())
        }

    def reset(self, content):
        self.raw_data = pd.SparseDataFrame(dtype=self.count_dtype)
        self.content = content
        self.vectorizer = None
        self.load_content(content)

    def rank_by_params(self, params):
        clean_params = self.clean_params(params)
        input_data = {self.features[key]: value for key, value in clean_params.items()}
        input_vector = pd.Series(data=input_data)
        data = self.data[list(input_data.keys())].dropna(how="all")
        data.fillna(0.0, inplace=True)
        ranking = data.dot(input_vector).sort_values(ascending=False)
        return ranking

    def clean_params(self, params):
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
