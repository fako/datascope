from itertools import chain

from spacy.language import Language
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class EntityDetector(object):

    def __init__(self, get_text, nlp):
        assert callable(get_text), "Expected get_text to be a callable"
        assert issubclass(nlp, Language), "nlp argument should be a spaCy Language model"
        self.get_text = get_text
        self.nlp = nlp
        self.entities = ["PERSON"]
        self.sorted_entities = {}

    def run(self, inputs, limit_per_entity=10):

        texts = [self.get_text(inp) for inp in inputs if self.get_text(inp)]
        for entity in self.entities:
            self.sorted_entities[entity] = self.get_entities(texts, entity)

        return {
            entity: [list(info) for info in serie[:limit_per_entity].items()]
            for entity, serie in self.sorted_entities.items()
        }

    def get_entity_tokenizer(self, entity):

        def entity_tokenizer(text):
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                if ent.label_ == entity and " " in ent.text:
                    entities.append(ent.text.replace(" ", "_"))
            return entities if len(entities) else ["NO_ENTITIES"]

        return entity_tokenizer

    def get_entities(self, texts, entity):
        vectorizer = TfidfVectorizer(
            tokenizer=self.get_entity_tokenizer(entity)
        )
        tfidf_entities = vectorizer.fit(texts)
        sorted_idf_entities = tfidf_entities.idf_.argsort()
        feature_names = vectorizer.get_feature_names()
        entities_data = dict(zip(feature_names, sorted_idf_entities))
        series = pd.Series(entities_data)
        series.sort_values(ascending=True, inplace=True)
        return series
        # vectors = vectorizer.transform(texts)
        # frame = pd.DataFrame(vectors.toarray(), columns=feature_names)




        # # Remove features that are in specified list
        # filtered = []
        # for feature in feature_names:
        #     for filter_feature in filter_features:
        #         if filter_feature in feature:
        #             filtered.append(feature)
        # frame.drop(labels=filtered, axis=1, inplace=True)
        # # As we're taking the whole corpus into account. What would it mean to use idf vector instead?
        # # It saves us a lot of memory
        # return frame.sum(axis=0) \
        #     .where(lambda value: value >= self.tfidf_treshold) \
        #     .dropna() \
        #     .sort_values(ascending=False)

    def _get_drop_index(self, ngram_series, ngram_history):
        drop_index = set()
        for ngram in chain(ngram_series, ngram_history):
            ngram_split = ngram.split(" ")
            drop_index.add(" ".join(ngram_split[0:-1]))
            drop_index.add(" ".join(ngram_split[1:]))
        return drop_index
