import spacy

from core.utils.text import ArguingLexiconParser

from topic_research.models import CrossCombineTermSearchCommunity
#from online_discourse.configurations.surveillance_laws import SINGULAR_SUBJECTS, PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES
from online_discourse.configurations.death_penalty import SINGULAR_SUBJECTS, PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES

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

        nlp = spacy.load('nl_core_news_sm')
        nlp.add_pipe(ArguingLexiconParser(lang=nlp.lang))

        for individual in out.individual_set.iterator():
            argument_count = 0
            sents_count = 0
            for paragraph_group in individual.properties.get("paragraph_groups", []):
                for doc in nlp.pipe(paragraph_group):
                    sents_count += len(list(doc.sents))
                    argument_spans = list(doc._.arguments.get_argument_spans())
                    argument_count += len(argument_spans)
            if sents_count:
                individual.properties["argument_score"] = argument_count / sents_count
                individual.clean()
                individual.save()

    class Meta:
        proxy = True
        verbose_name = "Discourse search community"
        verbose_name_plural = "Discourse search communities"
