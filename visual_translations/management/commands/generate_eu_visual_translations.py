from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands.grow_community import Command as GrowCommunityCommand

from sources.models import GoogleImage, GoogleTranslate


class Command(GrowCommunityCommand):

    community_model = "VisualTranslationsEUCommunity"

    def get_community(self):
        return self.model.objects.create_by_signature(self.signature, **self.config)

    def handle(self, *args, **kwargs):
        GoogleTranslate.objects.all().delete()
        GoogleImage.objects.all().delete()
        super(Command, self).handle(*args, **kwargs)
        self.model.objects.delete_manifestations_by_signature(signature=self.signature)
