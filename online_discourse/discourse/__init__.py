from collections import namedtuple


DiscourseConfiguration = namedtuple(
    "DiscourseConfiguration",
    ("title", "description", "language", "topics", "singular_subjects", "plural_subjects", "descriptive_adjectives",)
)
