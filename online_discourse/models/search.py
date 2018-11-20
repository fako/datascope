import logging
log = logging.getLogger(__name__)
import os
from collections import OrderedDict

try:
    import spacy
    from spacy_arguing_lexicon import ArguingLexiconParser
except ImportError:
    log.warn("Not supporting spacy on this platform")

import json_field

from core.models.organisms import Community, Collective, Individual
from core.models.organisms.states import CommunityState
from core.utils.helpers import cross_combine
from online_discourse.discourse import configurations


class DiscourseSearchCommunity(Community):

    aggregates = json_field.JSONField(default={})

    COMMUNITY_SPIRIT = OrderedDict([
        ("search", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#url",
            "config": {
                "_args": ["$.query", "$.quantity"],
                "_kwargs": {},
                "_resource": "GoogleText",
                "_objective": {
                    "@": "$.items",
                    "#term": "$.queries.request.0.searchTerms",
                    "title": "$.title",
                    "url": "$.link"
                },
                "_continuation_limit": 10,
                "_interval_duration": 1000
            },
            "schema": {},
            "errors": {},
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@search",
            "contribute": "Update:ExtractProcessor.pass_resource_through",
            "output": "@search",
            "config": {
                "_args": ["$.url"],
                "_kwargs": {},
                "_resource": "WebContentDownload",
                "_update_key": "url"
            },
            "schema": {},
            "errors": {},
        }),
        ("content", {
            "process": "ShellResourceProcessor.run_mass",
            "input": "@search",
            "contribute": "Inline:ExtractProcessor.extract_from_resource",
            "output": "@search",
            "config": {
                "_args": ["$.resourcePath"],
                "_kwargs": {},
                "_resource": "WebTextTikaResource",
                "_objective": {
                    "#resourcePath": "$.resourcePath",
                    "#title": "$.title",
                    "#language": "$.Content-Language",
                    "#content": "$.X-TIKA:content",
                    "#author": "$.author"
                },
                "_inline_key": "resourcePath"
            },
            "schema": {},
            "errors": {},
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "FilterProcessor.distinct",
            "config": {
                "distinct_key": "url"
            }
        },
        {
            "process": "FilterProcessor.select",
            "config": {
                "select_keys": ["author", "source"],
                "$author": None,
                "$source": None
            }
        },
        {
            "name": "rank",
            "process": "OnlineDiscourseRankProcessor.default_ranking",
            "config": {
                "$result_size": 60,
                "ranking_feature": "argument_score",
                "identifier_key": "url",
                "feature_frame_path": None,
                "text_frame_path": None,
                "$keywords": []
            }
        }
    ]

    SPACY_PACKAGES = {
        "en": "en_core_web_md",
        "nl": "nl_core_news_sm"
    }

    def initial_input(self, *args):
        configuration = getattr(configurations, args[0])
        combinations = cross_combine(
            configuration.singular_subjects + configuration.plural_subjects,
            configuration.descriptive_adjectives
        )
        collective = Collective.objects.create(community=self, schema={})
        for terms in combinations:
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "terms": "+".join(terms),
                    "query": " AND ".join(
                        [
                            '"{}"'.format(term) if not term.startswith("~") else term
                            for term in terms
                        ]
                    ),
                    "quantity": 10
                }
            )
        return collective

    def finish_download(self, out, err):
        out.identifier = "resourcePath"
        out.save()
        for entry in out.individual_set.all():
            entry.clean()
            entry.save()

    # def finish_download(self, out, err):
    #
    #     nlp = spacy.load(self.SPACY_PACKAGES[self.config.language])
    #     nlp.add_pipe(ArguingLexiconParser(lang=nlp.lang))
    #
    #     for individual in out.individual_set.iterator():
    #         argument_count = 0
    #         sents_count = 0
    #         paragraph_groups = individual.properties.get("paragraph_groups", [])
    #         if not paragraph_groups:
    #             continue
    #         for paragraph_group in paragraph_groups:
    #             for doc in nlp.pipe(paragraph_group):
    #                 sents_count += len(list(doc.sents))
    #                 argument_spans = list(doc._.arguments.get_argument_spans())
    #                 argument_count += len(argument_spans)
    #         if sents_count:
    #             individual.properties["argument_score"] = argument_count / sents_count
    #             individual.clean()
    #             individual.save()

    def set_kernel(self):
        self.kernel = self.current_growth.output

    def get_feature_frame_file(self, frame_type, file_ext=".pkl"):
        return os.path.join(self._meta.app_label, "data", frame_type + "s", self.signature + file_ext)

    def before_rank_manifestation(self, manifestation_part):
        manifestation_part["config"]["feature_frame_path"] = self.get_feature_frame_file("feature_frame")
        manifestation_part["config"]["text_frame_path"] = self.get_feature_frame_file("text_frame", ".npz")

    def store_frames(self):
        assert self.state == CommunityState.READY, "Can't store frames for a Community that is not ready"
        part = next((part for part in self.COMMUNITY_BODY if part.get("name") == "rank"), None)
        if part is None:
            raise TypeError("No RankProcessor part found in COMMUNITY_BODY")
        config = part.get("config")
        config["language"] = self.config.language
        rank_processor, method, args_type = self.prepare_process(part["process"], class_config=config)

        for frame_type in ["feature_frame", "text_frame"]:
            path, file_name = os.path.split(self.get_feature_frame_file(frame_type))
            if not os.path.exists(path):
                os.makedirs(path)

        rank_processor.feature_frame.load_content(lambda: self.kernel.content)
        rank_processor.feature_frame.to_disk(self.get_feature_frame_file("feature_frame"))

        rank_processor.text_frame.load_content(lambda: self.kernel.content)
        rank_processor.text_frame.to_disk(self.get_feature_frame_file("text_frame", file_ext=".npz"))

    def get_configuration_module(self):
        name = next((part for part in self.signature.split("&") if "=" not in part))
        return name, getattr(configurations, name, None)

    class Meta:
        verbose_name = "Discourse search community"
        verbose_name_plural = "Discourse search communities"
