from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "homosexual",
    "gay",
    "queer",
    "homophile",
    "lesbian",
    "lesbo",
    "family",
    "parent"
]

PLURAL_SUBJECTS = [
    "LGBT",
    "GLBT",
    "LGB",
    "LGBTQ",
    "straight",
    "gays",
    "lesbians",
    # "lesbos",
    "families",
    "parents",
    "mothers"
]

DESCRIPTIVE_ADJECTIVES = [
    "thread",
    "sick",
    "disease",
    "normal",
    "nature",
    "corner stone",
    "protection",
    "blessing",
    "perversion",
    "equal",
    "fascism",
    "evolution",
    "minorities"
    "minority",
    "orientation",
    "misrepresentation",
    "sex",
    "senseless",
    "species",
    "conservation",
    "adjust",
    "ban",
    "crusade",
    "contamination",
    "marriage",
    "rights",
    "couples",
    "flaw",
    "children",
    "adolescents",
    "society",
    "love",
    "religion",
    "march",
    "partnerships",
    "sin",
    "beating",
    "laws",
    "law",
    "organization",
    "worship",
    "sex",
    "shrine",
    "scripture",
    "hand in hand"

]

gay_rights = DiscourseConfiguration(
    language="en",
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
