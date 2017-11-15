import spacy

from core.utils.text import ArguingLexiconParser

from topic_research.models import CrossCombineTermSearchCommunity
from online_discourse.configurations.gayrights import SINGULAR_SUBJECTS, PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES


def arguing_lexicon_pipeline(nlp):
    return nlp.tagger, nlp.parser, nlp.entity, ArguingLexiconParser()


class DiscourseSearchCommunity(CrossCombineTermSearchCommunity):

    COMMUNITY_BODY = [
        {
            "process": "RankProcessor.score",
            "config": {
                "result_size": 60,
                "score_key": "argument_score"
            }
        }
    ]

    def initial_input(self, *args):
        return super(DiscourseSearchCommunity, self).initial_input(
            SINGULAR_SUBJECTS + PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES
        )

    def finish_download(self, out, err):
        nlp = spacy.load('en', create_pipeline=arguing_lexicon_pipeline)
        for individual in out.individual_set.iterator():
            argument_count = 0
            sents_count = 0
            for paragraph_group in individual.properties.get("paragraph_groups", []):
                for paragraph in paragraph_group:
                    doc = nlp(paragraph)
                    sents_count += len(list(doc.sents))
                    arguments = doc.user_data.get("arguments")
                    argument_spans = list(arguments.get_argument_spans())
                    argument_count += len(argument_spans)
            if sents_count:
                individual.properties["argument_score"] = argument_count / sents_count
                individual.clean()
                individual.save()

    class Meta:
        proxy = True
        verbose_name = "Discourse search community"
        verbose_name_plural = "Discourse search communities"
