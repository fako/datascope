from __future__ import unicode_literals, absolute_import, print_function, division

from django.db.models.manager import Manager


class CommunityManager(Manager):

    def get_latest_by_signature(self, signature, **kwargs):
        community = self.get_queryset().filter(signature=signature).latest("created_at")
        community.config = self.model.get_configuration_from_input(**kwargs)
        return community

    def create_by_signature(self, signature, **kwargs):
        return self.get_queryset().create(
            signature=signature,
            config=self.model.get_configuration_from_input(**kwargs)
        )

    def get_latest_or_create_by_signature(self, signature, **kwargs):
        created = False
        try:
            community = self.get_latest_by_signature(signature, **kwargs)
        except self.model.DoesNotExist:
            community = self.create_by_signature(signature, **kwargs)
            created = True
        return community, created

    def delete_manifestations_by_signature(self, signature):
        for community in self.get_queryset().filter(signature=signature):
            community.manifestation_set.all().delete()
