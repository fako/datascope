from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.db.models.manager import Manager


class CommunityManager(Manager):

    def get_by_signature(self, signature, **kwargs):
        community = self.get_queryset().get(signature=signature)
        community.config = self.model.get_configuration_through_input(**kwargs)
        return community

    def get_or_create_by_signature(self, signature, **kwargs):
        created = False
        try:
            community = self.get_by_signature(signature, **kwargs)
        except self.model.DoesNotExist:
            community = self.get_queryset().create(
                signature=signature,
                config=self.model.get_configuration_through_input(**kwargs)
            )
            created = True
        return community, created
