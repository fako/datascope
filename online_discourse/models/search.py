import os

import spacy
from spacy_arguing_lexicon import ArguingLexiconParser

from core.models.organisms.states import CommunityState
from topic_research.models import CrossCombineTermSearchCommunity
from online_discourse.discourse import configurations


class DiscourseSearchCommunity(CrossCombineTermSearchCommunity):

    COMMUNITY_BODY = [
        {
            "name": "rank",
            "process": "OnlineDiscourseRankProcessor.score",
            "config": {
                "result_size": 60,
                "ranking_feature": "argument_score",
                "identifier_key": "url",
                "feature_frame_path": None
            }
        }
    ]

    SPACY_PACKAGES = {
        "en": "en_core_web_md",
        "nl": "nl_core_news_sm"
    }

    PUBLIC_CONFIG = {
        "language": "en"
    }

    def initial_input(self, *args):
        configuration = getattr(configurations, args[0])
        return super(DiscourseSearchCommunity, self).initial_input(
            configuration.singular_subjects + configuration.plural_subjects, configuration.descriptive_adjectives
        )

    def finish_download(self, out, err):

        nlp = spacy.load(self.SPACY_PACKAGES[self.config.language])
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

    def get_feature_frame_file(self):
        return os.path.join(self._meta.app_label, "data", "feature_frames", self.signature + ".pkl")

    def before_rank_manifestation(self, manifestation_part):
        manifestation_part["config"]["feature_frame_path"] = self.get_feature_frame_file()

    def store_feature_frame(self):
        assert self.state == CommunityState.READY, "Can't store a frame for a Community that is not ready"
        path, file_name = os.path.split(self.get_feature_frame_file())
        if not os.path.exists(path):
            os.makedirs(path)

        part = next((part for part in self.COMMUNITY_BODY if part.get("name") == "rank"), None)
        if part is None:
            raise TypeError("No RankProcessor part found in COMMUNITY_BODY")
        rank_processor, method, args_type = self.prepare_process(part["process"], class_config=part.get("config"))
        rank_processor.feature_frame.load_content(lambda: self.kernel.content)
        rank_processor.feature_frame.to_disk(self.get_feature_frame_file())

    class Meta:
        proxy = True
        verbose_name = "Discourse search community"
        verbose_name_plural = "Discourse search communities"
