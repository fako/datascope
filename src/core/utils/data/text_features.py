import os
import pickle
from importlib import import_module

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.sparse import vstack, hstack, save_npz, load_npz


class TextContentReader(object):

    def __init__(self, get_identifier, get_text, content_callable):
        self.get_identifier = get_identifier
        self.get_text = get_text
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
        return self.get_text(entry)


class TextFeaturesFrame(object):

    def __init__(self, get_identifier, get_text, content=None, file_path=None, language="en"):
        self.get_identifier = get_identifier
        self.get_text = get_text
        self.language = language
        # Initialize attributes used by this class
        self.raw_data = None
        self.vectorizer = None
        self.data = None
        self.content = None
        self.features = None
        self.identifiers = None
        self.count_dtype = np.int16
        # Fill actual data frame with content
        if file_path:
            self.from_disk(file_path)
        elif content:
            self.reset(content=content)

    def from_disk(self, file_path):
        file_name, ext = os.path.splitext(file_path)
        self.raw_data = load_npz(file_path)
        with open(file_name + ".voc", "rb") as vocab_file:
            self.vectorizer = pickle.load(vocab_file)
        self.identifiers = pd.read_pickle(file_name + ".pkl")
        self.load_features(self.vectorizer)
        self.load_data(self.raw_data)

    def to_disk(self, file_path):
        file_name, ext = os.path.splitext(file_path)
        save_npz(file_path, self.raw_data)
        with open(file_name + ".voc", "wb") as vocab_file:
            pickle.dump(self.vectorizer, vocab_file)
        self.identifiers.to_pickle(file_name + ".pkl")

    def get_vectorizer(self):
        stop_words_module = import_module("spacy.lang.{}.stop_words".format(self.language))
        stop_words = list(getattr(stop_words_module, 'STOP_WORDS'))
        return CountVectorizer(stop_words=stop_words)

    def load_data(self, raw_data):
        transformer = TfidfTransformer()
        self.data = transformer.fit_transform(raw_data).tocsc()
        self.data /= self.data.max()  # min-max normalisation across columns with min=0

    def load_content(self, content_callable=None):
        if not self.vectorizer:
            self.vectorizer = self.get_vectorizer()
            should_fit = True
        else:
            should_fit = False
        content_reader = TextContentReader(self.get_identifier, self.get_text, content_callable or self.content)
        matrix = self.vectorizer.fit_transform(content_reader).tocsc() if should_fit \
            else self.vectorizer.transform(content_reader).tocsc()
        # Update existing data and deduplicate on index
        self.raw_data = vstack([self.raw_data, matrix]) if self.raw_data is not None else matrix
        if self.identifiers is None:
            self.identifiers = pd.Series(content_reader.identifiers)
        else:
            new = pd.Series(content_reader.identifiers)
            self.identifiers = self.identifiers.append(new) \
                .drop_duplicates(keep="last") \
                .reset_index(drop=True)
        # Converting the data to dok_matrix should deduplicate values
        # See: https://stackoverflow.com/questions/28677162/ignoring-duplicate-entries-in-sparse-matrix
        self.raw_data = self.raw_data.tocoo().todok().tocsc()
        self.load_data(self.raw_data)
        if should_fit:
            self.load_features(self.vectorizer)

    def load_features(self, vectorizer):
        self.features = {
            feature: ix
            for ix, feature in enumerate(vectorizer.get_feature_names())
        }

    def reset(self, content):
        self.raw_data = None
        self.content = content
        self.vectorizer = None
        self.load_content(content)

    def score_by_params(self, params):
        matrix = None
        vector = []
        for key, value in self.clean_params(params).items():
            col = self.data.getcol(self.features[key])
            matrix = hstack([matrix, col]) if matrix is not None else col
            vector.append(value)
        if matrix is None:
            return None
        vector = np.array(vector)
        values = matrix.dot(vector)
        return pd.Series(values, index=self.identifiers)

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
