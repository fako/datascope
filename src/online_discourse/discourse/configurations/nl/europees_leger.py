from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "Wapenhandelaar",
    "Wapenindustrie",
    "Vredesactivist",
    "Regering",
    "Media",
    "Parlement",
    "Generaal",
    "Diplomaat",
    "Soldaat",
    "Wapenlobby",
    "NAVO",
    "Europese Unie",
    "Verenigde Naties",
    "Poetin",
    "China",
    "Marine",
    "Defensie",
    "Luchtmacht",
    "OVSE",
    "Schiphol",
    "Stork",
    "Damen Shipyards",
    "TNO",
    "Universiteit",
    "Airbus",
    "Instituut Clingendael",
    "Europese Commissie",
    "Raad van Europa",
    "Europees Parlement",
    "Europese Raad",
]

PLURAL_SUBJECTS = [
    "Vredesactivisten",
    "Diplomaten",
    "Universiteiten",
    "Soldaten",
]

DESCRIPTIVE_ADJECTIVES = [
    "Wapenwedloop",
    "Minder soevereiniteit",
    "Band met Afrika",
    "Economische schade",
    "Onenigheid lidstaten",
    "NAVO is sterker",
    "bodybags",
    "Veiligheid",
    "Macht",
    "Binding lidstaten",
    "Samenwerking lidstaten",
    "budget",
    "Europe first",
    "ontwikkeling van de EU",
    "3D-diplomacy",
    "Sterker tegenover Poetin",
    "Sterker tegenover Erdogan",
    "Conflict Oekraïne is oplosbaar",
    "Supranationale besluitvorming",
    "Vrede",
    "Banen",
    "Export",
    "Industrieel militair complex",
    "cohesie",
]

europees_leger = DiscourseConfiguration(
    title="Europees leger",
    description="Er is veel kritiek op de Europese Unie. "
                "Toch zijn er ook geluiden, die aangeven dat we meer zouden moeten samenwerken op Europees niveau. "
                "Bijvoorbeeld op militair gebied.",
    language="nl",
    topics=["leger"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
