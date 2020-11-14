from elasticsearch.helpers import streaming_bulk

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField
from rest_framework import serializers

from online_discourse.models import DiscourseSearchCommunity
from online_discourse.elastic import get_index_config, get_es_client


elastic_client = get_es_client(silent=True)


class ElasticIndex(models.Model):

    signature = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.ELASTIC_SEARCH_ANALYSERS.items())
    dataset = models.ForeignKey(DiscourseSearchCommunity, related_name="indices")
    configuration = JSONField(blank=True)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = elastic_client

    @property
    def remote_name(self):
        if not self.id:
            raise ValueError("Can't get the remote name for an unsaved object")
        return slugify("{}-{}-{}".format(self.signature, self.language, self.id))

    @property
    def remote_exists(self):
        if not self.id:
            raise ValueError("Can't check for existence with an unsaved object")
        return self.client.indices.exists(self.remote_name)

    def push(self, elastic_documents, recreate=True, request_timeout=300):  # why is the elastic cluster usually slow?
        if not self.id:
            raise ValueError("Can't push index with unsaved object")

        remote_name = self.remote_name
        if self.remote_exists and recreate:
            self.client.indices.delete(remote_name)

        self.client.indices.create(
            index=remote_name,
            body=self.configuration,
            request_timeout=request_timeout
        )
        if recreate:
            self.error_count = 0
        for is_ok, result in streaming_bulk(self.client, elastic_documents, index=remote_name, doc_type="_doc",
                                            chunk_size=100, yield_ok=False, raise_on_error=False,
                                            request_timeout=request_timeout):
            if not is_ok:
                self.error_count += 1
                print(f'Error in sending bulk:{result}')
        self.save()

    def promote_to_latest(self):
        latest_alias = "latest-" + self.language
        if self.client.indices.exists_alias(name=latest_alias):
            self.client.indices.delete_alias(index="_all", name=latest_alias)
        self.client.indices.put_alias(index=self.remote_name, name=latest_alias)

    def clean(self):
        if not self.signature:
            self.signature = self.dataset.signature
        if self.language and not self.configuration:
            self.configuration = get_index_config(self.language)

    def __str__(self):
        return self.signature

    class Meta:
        verbose_name = "elastic index"
        verbose_name_plural = "elastic indices"


class ElasticIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElasticIndex
        fields = ("id", "signature", "language", "remote_name",)
