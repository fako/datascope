from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "Europese Unie",
    "Jellinek",
    "Festival",
    "politie",
    "GGZ",
    "Leger des Heils",
    "D66",
    "VVD",
    "Groen Links",
    "SGP",
    "CDA",
    "PvdD",
    "PvdA",
    "Religie",
    "Junk",
    "Gebruiker",
    "Crimineel",
    "Drugsbaron",
    "Cartel",
]

PLURAL_SUBJECTS = [
    "Coffeeshops",
    "Lidstaten",
    "Criminele organisaties",
    "Ziekenhuizen",
    "Artsen",
    "Scholen",
    "BN-ers",
    "bekende Nederlanders",
    "Ouders",
    "Influencers",
]

DESCRIPTIVE_ADJECTIVES = [
    "afname criminaliteit",
    "vrije keuze",
    "Medicijn",
    "economie",
    "zwartgeldcircuit",
    "Kwaliteitsgarantie",
    "gevangenen",
    "oorlog tegen drugs",
    "goedkoper",
    "medicinaal",
    "Volksgezondheid",
    "Verslaving",
    "Medische kosten",
    "jeugdbescherming",
    "Criminaliteit verschuift",
    "gateway drug",
    "diplomatie",
    "Milieuschade",
    "Stepping stone",
    "harde criminaliteit",
    "Zonde",
    "haram",
    "handel",
    "Verbod",
]

drugs_legalisatie = DiscourseConfiguration(
    title="Drugs legalisatie",
    description="Nederland kent al heel lang een gedoog beleid waarbij de verkoop van softdrugs is toegestaan, "
                "maar de inkoop niet. Men spreekt al een tijd over het geheel legaliseren van softdrugs, "
                "maar tot nu toe zonder resultaat.",
    language="nl",
    topics=["drugs", "softdrugs"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
