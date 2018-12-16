from spacy.language import Language
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class EntityDetector(object):

    def __init__(self, get_text, nlp):
        assert callable(get_text), "Expected get_text to be a callable"
        assert isinstance(nlp, Language), "nlp argument should be a spaCy Language model"
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
        entities_matrix = vectorizer.fit_transform(texts)
        tfidf_entities_matrix = entities_matrix.sum(axis=0)
        tfidf_entities = tfidf_entities_matrix.tolist()[0]
        feature_names = vectorizer.get_feature_names()
        entities_data = dict(zip(feature_names, tfidf_entities))
        series = pd.Series(entities_data)
        series.sort_values(ascending=False, inplace=True)
        return series
