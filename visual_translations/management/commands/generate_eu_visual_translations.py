from core.management.commands.grow_community import Command as GrowCommunityCommand

from sources.models import GoogleImage, GoogleTranslate


class Command(GrowCommunityCommand):

    community_model = "VisualTranslationsEUCommunity"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--delete', action="store_true")

    def get_community(self):
        return self.model.objects.create_by_signature(self.signature, **self.config)

    def handle(self, *args, **options):
        if options["delete"]:
            GoogleTranslate.objects.all().delete()
            GoogleImage.objects.all().delete()
        super(Command, self).handle(*args, **options)
        self.model.objects.delete_manifestations_by_signature(signature=self.signature)
