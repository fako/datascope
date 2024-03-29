from spacy.language import Language
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class EntityDetector(object):

    def __init__(self, get_text, nlp):
        assert callable(get_text), "Expected get_text to be a callable"
        assert isinstance(nlp, Language), "nlp argument should be a spaCy Language model"
        self.get_text = get_text
        self.nlp = nlp
        self.nlp.max_length = 50000  # arbitrary, prevents memory errors, see: entity_tokenizer
        self.entities = ["PERSON"]
        self.sorted_entities = {}

    def run(self, inputs, limit_per_entity=10):

        texts = [self.get_text(inp) for inp in inputs if self.get_text(inp)]
        for entity in self.entities:
            self.sorted_entities[entity] = self.get_entities(texts, entity)

        results = {}
        for entity, serie in self.sorted_entities.items():
            results[entity] = []
            for name, count in serie[:limit_per_entity].items():
                if name == "NO_ENTITIES":
                    continue
                results[entity].append([name, count])

        return results

    def get_entity_tokenizer(self, entity):

        def entity_tokenizer(text):  # TODO: detect as pipe instead of cating entire document
            doc = self.nlp(text[:self.nlp.max_length])  # limit is for spaCy memory usage
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
        entities_matrix = vectorizer.fit_transform(texts)
        tfidf_entities_matrix = entities_matrix.sum(axis=0)
        tfidf_entities = tfidf_entities_matrix.tolist()[0]
        feature_names = vectorizer.get_feature_names()
        entities_data = dict(zip(feature_names, tfidf_entities))
        series = pd.Series(entities_data)
        series.sort_values(ascending=False, inplace=True)
        return series
