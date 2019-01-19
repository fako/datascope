import logging
log = logging.getLogger(__name__)
import os
from collections import OrderedDict
from urlobject import URLObject
from tqdm import tqdm

try:
    import spacy
    from spacy_arguing_lexicon import ArguingLexiconParser
    from spacy.lang.nl.stop_words import STOP_WORDS as NL_STOP_WORDS
except ImportError:
    NL_STOP_WORDS = []
    log.warn("Not supporting spacy on this platform")

from django.db.models import Q
import json_field

from core.models.organisms import Community, Collective, Individual
from core.models.organisms.states import CommunityState
from core.utils.helpers import cross_combine
from online_discourse.models.sources import WebTextTikaResource
from online_discourse.discourse import configurations
from online_discourse.processors import TopicDetector, EntityDetector, OnlineDiscourseRankProcessor


class DiscourseSearchCommunity(Community):

    aggregates = json_field.JSONField(default={}, blank=True)

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
                "_update_key": "url",
                "$language": "en"
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
            "process": "FilterProcessor.filter",
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
        "en": "en_core_web_lg",
        "nl": "nl_core_news_sm"
    }
    STOP_WORDS = {
        "en": "english",  # grabs sklearn stopwords
        "nl": NL_STOP_WORDS
    }
    NON_TOPICS = {
        "en": [],
        "nl": ["cookies", "website", "browser", "advertenties"]
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

    def finish_search(self, out, err):
        total = out.individual_set.count()
        current_entry = None
        deletes = []
        for entry in tqdm(out.individual_set.order_by("identity").iterator(), total=total):
            if current_entry is None or current_entry.identity != entry.identity:
                if current_entry is not None:
                    current_entry.save()
                if len(deletes):
                    out.individual_set.filter(id__in=deletes).delete()
                current_entry = entry
                deletes = []
                if isinstance(current_entry.properties["term"], str):
                    current_entry.properties["term"] = [current_entry.properties["term"]]
            else:
                current_entry.properties["term"].append(entry.properties["term"])
                deletes.append(entry.id)

    def finish_download(self, out, err):
        out.identifier = "resourcePath"
        out.save()
        total = out.individual_set.count()
        for entry in tqdm(out.individual_set.iterator(), total=total):
            entry.clean()
            entry.save()
        deletes = out.individual_set.filter(identity__isnull=True).delete()
        log.info(deletes)

        # Now that text has been extracted. Delete irrelevant entries not about specified topics
        name, configuration = self.get_configuration_module()
        query_filter = Q()
        for topic in configuration.topics:
            query_filter |= Q(properties__icontains=topic)
        deletes = out.individual_set.exclude(query_filter).delete()
        log.info(deletes)

    def finish_content(self, out, err):

        spacy_parsers = {}
        for language, package in self.SPACY_PACKAGES.items():
            nlp = spacy.load(package)
            nlp.add_pipe(ArguingLexiconParser(lang=nlp.lang))
            spacy_parsers[language] = nlp

        # File paths to downloads is not a useful identifier after dataset creation
        # Resetting to source URL
        out.identifier = "url"
        out.save()
        total = out.individual_set.count()

        for individual in tqdm(out.individual_set.iterator(), total=total):

            if individual.properties.get("source", None):
                continue

            source = URLObject(individual.properties["url"]).hostname
            if source.startswith("www."):
                source = source.replace("www.", "", 1)
            individual.properties["source"] = source

            # Checking if there is any content data to work with.
            # Then undoing a weird hack where content data gets stored under resourcePath
            # It happens because inline_key and identifier need to match
            # TODO: allow inline_key to be different from identifier
            data = individual.properties.get("resourcePath", None)
            if not isinstance(data, dict):
                individual.clean()
                individual.save()
                continue

            author = data.get("author", None)
            if author and isinstance(author, str):
                pass
            elif author:
                author = author[0]  # TODO: we take the primary author now, but should also consider other authors
            else:
                author = None
            individual.properties["author"] = author

            titles, paragraphs, junk = WebTextTikaResource.extract_texts(data.get("title"), data.get("content"))
            del data["content"]
            data["titles"] = titles
            data["paragraphs"] = paragraphs
            data["junk"] = junk
            individual.properties["content"] = data
            del individual.properties["resourcePath"]

            # Lots of code still depends on a property named "paragraph_groups".
            # This was used in an early version of text extraction
            # We mimick it here to keep backwards compatability
            # TODO: migrate code away from paragraph_groups
            content = titles + paragraphs
            if not len(content):
                individual.clean()
                individual.save()
                continue
            paragraph_groups = [content]
            individual.properties["paragraph_groups"] = paragraph_groups

            nlp = spacy_parsers[self.config.language]
            argument_count = 0
            sents_count = 0
            for doc in nlp.pipe(content):
                sents_count += len(list(doc.sents))
                argument_spans = list(doc._.arguments.get_argument_spans())
                argument_count += len(argument_spans)
            if sents_count:
                individual.properties["argument_score"] = argument_count / sents_count

            individual.clean()
            individual.save()

        # And finally calculate the aggregates
        self.set_aggregates(out)
        self.save()

    def set_aggregates(self, collection):
        self.aggregates.update(
            self.get_source_and_author_aggregates(collection)
        )
        self.aggregates.update(
            self.get_topic_aggregates(collection)
        )
        self.aggregates.update(
            self.get_entity_aggregates(collection)
        )

    def get_source_and_author_aggregates(self, collection):
        sources = set()
        authors = set()
        for individual in collection.individual_set.iterator():
            sources.add(individual.properties.get("source", None))
            author = individual.properties.get("author", None)
            if author:
                authors.add(author)
        return {
            "authors": sorted(list(authors)),
            "sources": sorted(list(sources))
        }

    def get_topic_aggregates(self, collection):
        detector = TopicDetector(
            OnlineDiscourseRankProcessor.get_text,
            stop_words=list(self.STOP_WORDS[self.config.language]),
            filter_words=self.NON_TOPICS[self.config.language]
        )
        return {
            "most_important_words": detector.run(collection.content)
        }

    def get_entity_aggregates(self, collection):
        nlp = spacy.load(self.SPACY_PACKAGES[self.config.language])
        detector = EntityDetector(
            OnlineDiscourseRankProcessor.get_text,
            nlp
        )
        return {
            "entities": detector.run(collection.content)
        }

    def set_kernel(self):
        self.kernel = self.current_growth.output

    def get_feature_frame_file(self, frame_type, file_ext=".pkl"):
        return os.path.join("data", self._meta.app_label, frame_type + "s", self.signature + file_ext)

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
