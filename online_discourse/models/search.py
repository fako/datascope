from topic_research.models import CrossCombineTermSearchCommunity
from online_discourse.configurations.immigrants import SINGULAR_SUBJECTS, PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES


class DiscourseSearchCommunity(CrossCombineTermSearchCommunity):

    def initial_input(self, *args):
        return super(DiscourseSearchCommunity, self).initial_input(
            SINGULAR_SUBJECTS + PLURAL_SUBJECTS, DESCRIPTIVE_ADJECTIVES
        )

    class Meta:
        proxy = True
        verbose_name = "Discourse search community"
        verbose_name_plural = "Discourse search communities"
