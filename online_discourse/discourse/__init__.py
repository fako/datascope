from collections import namedtuple


DiscourseConfiguration = namedtuple(
    "DiscourseConfiguration",
    ("title", "description", "language", "singular_subjects", "plural_subjects", "descriptive_adjectives",)
)
