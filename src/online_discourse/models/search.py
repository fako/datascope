import logging
log = logging.getLogger("datagrowth.command")
import os
from collections import OrderedDict
from urlobject import URLObject
from tqdm import tqdm
from bs4 import BeautifulSoup
from bs4.element import NavigableString

try:
    import spacy
    from spacy_arguing_lexicon import ArguingLexiconParser
    from spacy.lang.nl.stop_words import STOP_WORDS as NL_STOP_WORDS
except ImportError:
    NL_STOP_WORDS = []
    log.warning("Not supporting spacy on this platform")

from django.db.models import Q
import json_field

from datagrowth.utils import get_model_path
from datagrowth.resources import HttpResource
from core.models.organisms import Community, CommunityCollectionDocumentMixin
from core.models.organisms.states import CommunityState
from core.utils.helpers import cross_combine
from online_discourse.models import Collection, Document
from online_discourse.discourse import configurations
from online_discourse.processors import TopicDetector, EntityDetector, OnlineDiscourseRankProcessor


class DiscourseSearchCommunity(CommunityCollectionDocumentMixin, Community):

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"

    aggregates = json_field.JSONField(default={}, blank=True)

    COMMUNITY_SPIRIT = OrderedDict([
        ("search", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collection#url",
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
        ("download_article", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@search",
            "contribute": "Update:ExtractProcessor.pass_resource_through",
            "output": "@search",
            "config": {
                "_args": ["$.url"],
                "_kwargs": {},
                "_resource": "WebContentDownload",
                "_update_key": "url",
                "$language": "en",  # TODO: think of a way to include language as a parameter without using config
                # Keys below are used by WebContentDownload to format its output
                "resource_key": "resourcePath",
                "user_agent": USER_AGENT
            },
            "schema": {},
            "errors": {},
        }),
        ("download_home", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@search",
            "contribute": "Update:ExtractProcessor.pass_resource_through",
            "output": "@search",
            "config": {
                "_args": ["$.home"],
                "_kwargs": {},
                "_resource": "WebContentDownload",
                "_update_key": "home",
                # Keys below are used by WebContentDownload to format its output
                "url_key": "home",
                "resource_key": "home_resource",
                "user_agent": USER_AGENT
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
                    "#author": "$.author",
                    "#content_type": "$.Content-Type"
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

    DATAGROWTH = True

    SPACY_PACKAGES = {
        "en": "en_core_web_lg",
        "nl": "nl_core_news_sm"
    }
    STOP_WORDS = {
        "en": "english",  # grabs sklearn stopwords
        "nl": NL_STOP_WORDS
    }
    NON_TOPICS = {
        "en": ["window", "story", "facebook", "twitter", "email", "search", "tweet"],
        "nl": ["categorie", "tagarchief", "link"]
    }

    def initial_input(self, *args):
        configuration = getattr(configurations, args[0])
        combinations = cross_combine(
            configuration.singular_subjects + configuration.plural_subjects,
            configuration.descriptive_adjectives
        )
        collection = Collection.objects.create(community=self, schema={})
        for terms in combinations:
            Document.objects.create(
                community=self,
                collection=collection,
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
        return collection

    def _set_source_data(self, document):
        url = URLObject(document.properties["url"])
        source = url.hostname
        if source.startswith("www."):
            source = source.replace("www.", "", 1)
        document.properties["source"] = source
        document.properties["home"] = "{}://{}".format(url.scheme, url.hostname)
        return document

    def _set_main_content(self, document):

        # Loading data
        data = document.properties.get("tika", {}) or {}
        content_type = data.get("content_type", "text/html")
        mime_type, encoding = HttpResource.parse_content_type(content_type)
        if not mime_type.startswith("text/html"):
            document["content"] = data.get("content", "") or ""  # prevents None
            document["content"] = document["content"].split("\n")
            return document
        try:
            with open(data["resourcePath"], encoding=encoding) as fp:
                article = BeautifulSoup(fp, "html5lib")
            with open(document.properties["home_resource"], encoding=encoding) as fp:
                home = BeautifulSoup(fp, "html5lib")
        except FileNotFoundError:
            log.warning("Missing a file for document: {}".format(document.id))
            document["content"] = []
            return document
        except UnicodeDecodeError:
            log.warning("Encoding error with file for document: {}".format(document.id))
            document["content"] = []
            return document
        except KeyError:
            log.warning("Key error with file for document when setting main content: {}".format(document.id))
            document["content"] = []
            return document
        except LookupError:
            log.warning("Lookup error with file encoding for document when setting main content: {}".format(document.id))
            document["content"] = []
            return document

        # Calculate text diff between home, article and Tika
        raw_content = data.get("content", "")  # prevents None with empty content
        home_contents = set()
        for el in home.descendants:
            if not isinstance(el, NavigableString):
                continue
            text = el.string.strip()
            if text:
                home_contents.add(text)
        article_contents = []
        junk_contents = []
        for el in article.descendants:
            if not isinstance(el, NavigableString):
                continue
            text = el.string.strip()
            if text and text not in home_contents and isinstance(text, str):
                if text in raw_content:
                    article_contents += text.split("\n")
                else:
                    junk_contents += text.split("\n")

        document.properties["junk"] = junk_contents
        document.properties["content"] = article_contents
        return document

    def _set_author(self, document):
        data = document.properties.get("tika", {})
        author = data.get("author", None)
        if author and isinstance(author, str):
            pass
        elif author:
            author = author[0]  # TODO: we take the primary author now, but should also consider other authors
        else:
            author = None
        document.properties["author"] = author
        return document

    def finish_search(self, out, err):
        log.info("Filter duplicates, save source and delete invalid")
        total = out.documents.count()
        current_entry = None
        deletes = []
        # Filter out duplicates, but keep track of terms where pages were found
        # It also sets the source and home page URL for each result
        for entry in tqdm(out.documents.order_by("identity").iterator(), total=total):
            if current_entry is None or current_entry.identity != entry.identity:
                if current_entry is not None:
                    current_entry = self._set_source_data(current_entry)
                    current_entry.save()
                if len(deletes):
                    out.documents.filter(id__in=deletes).delete()
                current_entry = entry
                deletes = []
                if isinstance(current_entry.properties["term"], str):
                    current_entry.properties["term"] = [current_entry.properties["term"]]
            else:
                current_entry.properties["term"].append(entry.properties["term"])
                deletes.append(entry.id)
        # Removing invalid entries
        deletes = out.documents.filter(identity__isnull=True).delete()
        log.info("Deletes: {}".format(deletes))

    def begin_download_home(self, out):
        log.info("Resetting identifier to 'home' and delete invalid")
        out.identifier = "home"
        out.save()
        total = out.documents.count()
        for entry in tqdm(out.documents.iterator(), total=total):
            entry.clean()
            entry.save()
        # Removing invalid entries
        deletes = out.documents.filter(identity__isnull=True).delete()
        log.info("Deletes: {}".format(deletes))

    def begin_content(self, out):
        # NB: non-content differs from empty content
        log.info("Resetting identifier to 'resourcePath' and deleting non-content entries")
        out.identifier = "resourcePath"
        out.save()
        total = out.documents.count()
        for entry in tqdm(out.documents.iterator(), total=total):
            entry.clean()
            entry.save()
        assert total != out.documents.filter(identity__isnull=True).count(), \
            "At begin_content there are no documents with any content. Aborting"
        deletes = out.documents.filter(identity__isnull=True).delete()
        log.info("Deletes: {}".format(deletes))

    def finish_content(self, out, err):
        log.info("Deleting entries that are off topic entirely")
        # Now that text has been extracted. Delete irrelevant entries not about specified topics
        name, configuration = self.get_configuration_module()
        query_filter = Q()
        for topic in configuration.topics:
            query_filter |= Q(properties__icontains=topic)
        deletes = out.documents.exclude(query_filter).delete()
        log.info("Deletes: {}".format(deletes))

        log.info("Resetting identifier to 'url', cleaning output and deleting invalids")
        # File paths to downloads is not a useful identifier after dataset creation
        # Resetting to source URL
        out.identifier = "url"
        out.save()
        total = out.documents.count()
        invalids = []
        for document in tqdm(out.documents.iterator(), total=total):
            # Skip reset when it has already been done
            if document.properties.get("tika", None):
                continue
            # Checking if there is any content data to work with.
            # Then undoing a weird hack where content data gets stored under resourcePath
            # It happens because inline_key and identifier need to match
            # TODO: allow inline_key to be different from identifier
            data = document.properties.get("resourcePath", {})
            if isinstance(data, str):
                log.warning("resourcePath not replaced by dict: {}".format(document.id))
                continue
            document.properties["tika"] = data
            content = data.get("content", "")
            # We're only keeping the content that actually holds topics of interest.
            if not data or not content:
                invalids.append(document.id)
                continue
            for topic in configuration.topics:
                if topic in content:
                    break
            else:
                invalids.append(document.id)
                continue

            del document.properties["resourcePath"]
            document.clean()
            document.save()
        deletes = out.documents.filter(id__in=invalids).delete()
        log.info("Deletes: {}".format(deletes))

        #################################################################################
        # TODO: The next phases are better handled by a process_mini_batch task
        #################################################################################

        log.info("Parsing content")
        # Preparation by loading spaCy
        spacy_parsers = {}
        for language, package in self.SPACY_PACKAGES.items():
            if language == self.config.language:  # TODO: allow multiple languages in arguing lexicon package
                nlp = spacy.load(package)
                nlp.add_pipe(ArguingLexiconParser(lang=nlp.lang))
                spacy_parsers[language] = nlp
        # Actual content extraction
        off_topics = []
        for document in tqdm(out.documents.iterator(), total=total):

            # We're skipping any entries that have already been processed at some point
            if document.properties.get("argument_score", None) is not None:
                continue

            # Now we turn raw content into something consistent set on the document
            document = self._set_author(document)
            document = self._set_main_content(document)

            # Lots of code still depends on a property named "paragraph_groups".
            # This was used in an early version of text extraction
            # We mimick it here to keep backwards compatability
            # TODO: migrate code away from paragraph_groups
            content = document.properties.get("content")
            if not len(content):
                document.clean()
                document.save()
                continue
            document.properties["paragraph_groups"] = [content]

            nlp = spacy_parsers[self.config.language]
            argument_count = 0
            sents_count = 0
            for doc in nlp.pipe(content):
                sents_count += len(list(doc.sents))
                argument_spans = list(doc._.arguments.get_argument_spans())
                argument_count += len(argument_spans)
            if sents_count:
                document.properties["argument_score"] = argument_count / sents_count

            document.clean()
            document.save()

        #################################################################################
        # Handling aggregations which is not supported by the framework at this time
        #################################################################################

        self.set_aggregates(out)
        self.save()

    def set_aggregates(self, collection):
        log.info("Aggregating sources and authors")
        self.aggregates.update(
            self.get_source_and_author_aggregates(collection)
        )
        log.info("Aggregating topics")
        self.aggregates.update(
            self.get_topic_aggregates(collection)
        )
        log.info("Aggregating entities")
        self.aggregates.update(
            self.get_entity_aggregates(collection)
        )

    def get_source_and_author_aggregates(self, collection):
        sources = set()
        authors = set()
        for document in collection.documents.iterator():
            sources.add(document.properties.get("source", None))
            author = document.properties.get("author", None)
            if author:
                authors.add(author)
        return {
            "authors": sorted(list(authors)),
            "sources": sorted(list(sources))
        }

    def get_topic_aggregates(self, collection):

        stop_words = self.STOP_WORDS[self.config.language]
        if not isinstance(stop_words, (str, list)):
            type(stop_words)
            stop_words = list(stop_words)

        detector = TopicDetector(
            OnlineDiscourseRankProcessor.get_text,
            stop_words=stop_words,
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
        model_path = get_model_path( self._meta.app_label, frame_type + "s")
        return os.path.join(model_path, self.signature + file_ext)

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
