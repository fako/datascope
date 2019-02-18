import json
from collections import Iterator, Iterable

from django.apps import apps
from django.db import models
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from datagrowth.datatypes.documents.base import DataStorage
from datagrowth.utils import ibatch, reach


class CollectionBase(DataStorage):

    name = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    referee = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def get_document_model(cls):
        # This method should use "Document" with local app label and get_model function to load the model
        return apps.get_model("{}.Document".format(cls._meta.app_label))

    @property
    def documents(self):
        # This method should be smart about returning the correct document_set
        Document = self.get_document_model()
        return Document.objects.all()

    def init_document(self, data, collection=None):
        Document = self.get_document_model()
        return Document(
            schema=self.schema,
            properties=data
        )

    @classmethod
    def validate(cls, data, schema):
        """
        Validates the data against given schema for one of more Documents.

        :param data: The data to validate
        :param schema: The JSON schema to use for validation.
        :return: Valid data
        """
        Document = cls.get_document_model()
        if not isinstance(data, Iterable):
            data = [data]
        for instance in data:
            Document.validate(instance, schema)

    def add(self, data, validate=True, reset=False, batch_size=500, collection=None):
        """
        Update the instance with new data by adding to the Collection
        or by updating Documents that members off the Collection.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: A list of updated or created instances.
        """
        collection = collection or self
        Document = self.get_document_model()
        assert isinstance(data, (Iterator, list, tuple, dict, Document)), \
            "Collection.update expects data to be formatted as iteratable, dict or Document not {}".format(type(data))

        if reset:
            self.documents.all().delete()

        def prepare_updates(data):

            prepared = []
            if isinstance(data, dict):
                if validate:
                    Document.validate(data, self.schema)
                document = self.init_document(data, collection=collection)
                document.clean()
                prepared.append(document)
            elif isinstance(data, Document):
                if validate:
                    Document.validate(data, self.schema)
                data = self.init_document(data.properties, collection=collection)
                data.clean()
                prepared.append(data)
            else:  # type is list
                for instance in data:
                    prepared += prepare_updates(instance)
            return prepared

        count = 0
        for updates in ibatch(data, batch_size=batch_size):
            updates = prepare_updates(updates)
            count += len(updates)
            Document.objects.bulk_create(updates, batch_size=settings.MAX_BATCH_SIZE)

        return count

    @property
    def content(self):
        """
        Returns the content of the documents of this Collection

        :return: a generator yielding properties from Documents
        """
        return (ind.content for ind in self.documents.iterator())

    @property
    def has_content(self):
        """
        Indicates if Collection entails Documents or not

        :return: True if there are Documents, False otherwise
        """
        return self.documents.exists()

    @property
    def json_content(self):
        json_content = [ind.json_content for ind in self.documents.all()]
        return "[{}]".format(",".join(json_content))

    def split(self, train=0.8, validate=0.1, test=0.1, query_set=None, as_content=False):  # TODO: test to unlock
        assert train + validate + test == 1.0, "Expected sum of train, validate and test to be 1"
        assert train > 0, "Expected train set to be bigger than 0"
        assert validate > 0, "Expected validate set to be bigger than 0"
        query_set = query_set or self.documents
        content_count = query_set.count()
        # TODO: take into account that random ordering in MySQL is a bad idea
        # Details: http://www.titov.net/2005/09/21/do-not-use-order-by-rand-or-how-to-get-random-rows-from-table/
        documents = query_set.order_by("?").iterator()
        test_set = []
        if test:
            test_size = round(content_count * test)
            test_set = [next(documents) for ix in range(0, test_size)]
        validate_size = round(content_count * validate)
        validate_set = [next(documents) for ix in range(0, validate_size)]
        return (
            (document.content if as_content else document for document in documents),
            [document.content if as_content else document for document in validate_set],
            [document.content if as_content else document for document in test_set]
        )

    def output(self, *args):
        if len(args) > 1:
            return map(self.output, args)
        frm = args[0]
        if not frm:
            return [frm for ind in range(0, self.documents.count())]
        elif isinstance(frm, list):
            output = self.output(*frm)
            if len(frm) > 1:
                output = [list(zipped) for zipped in zip(*output)]
            else:
                output = [[out] for out in output]
            return output
        else:
            return [ind.output(frm) for ind in self.documents.iterator()]

    def group_by(self, key):
        """
        Outputs a dict with lists. The lists are filled with Documents that hold the same value for key.

        :param key:
        :return:
        """
        grouped = {}
        for ind in self.documents.all():
            assert key in ind.properties, \
                "Can't group by {}, because it is missing from an document in collection {}".format(key, self.id)
            value = ind.properties[key]
            if value not in grouped:
                grouped[value] = [ind]
            else:
                grouped[value].append(ind)
        return grouped

    def influence(self, document):
        """
        This allows the Collection to set some attributes and or properties on the Document

        :param document: The document that should be influenced
        :return: The influenced document
        """
        if self.identifier:
            document.identity = reach("$." + self.identifier, document.properties)
            document.reference = reach("$." + self.referee, document.properties)
        return document

    def to_file(self, file_path):
        with open(file_path, "w") as json_file:
            json.dump(list(self.content), json_file, cls=DjangoJSONEncoder)

    class Meta:
        abstract = True
        get_latest_by = "created_at"
        ordering = ["created_at"]
