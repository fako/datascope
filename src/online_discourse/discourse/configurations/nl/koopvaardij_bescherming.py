from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "staat",
    "verzekeraar",
    "koopvaardij",
    "piraat",
    "militair",
    "marine",
    "schip",
    "somalie",
    "somalië",
    "beveiliger",
    "Koninklijke Vereniging van Nederlandse Reders",
    "KVNR",
    "Koninklijke Marine",
    "Ministerie van Defensie",
    "Verbond van Verzekeraars",
    "PAX",
    "TNI",
    "AOU",
    "Ministerie van Veiligheid en Justitie",
    "private military companies"
]

PLURAL_SUBJECTS = [
    "staten",
    "landen",
    "verzekeraars",
    "piraten",
    "militairen",
    "mariniers",
    "schepen",
    "beveiligers"
]

DESCRIPTIVE_ADJECTIVES = [
    "piraterij",
    "private",
    "geweld",
    "bescherming",
    "gewapend",
    "geweldadig",
    "veiligheid",
    "handel",
    "kosten",
    "geld",
    "losgeld",
    "belastinginkomsten",
    "geweldsmonopolie",
    "zwaardmacht",
    "symptoombestrijding",
    "juridisch",
    "wapen wedloop",
    "anti-piraterij",
    "scheepvaart",
    "handelsbelangen",
    "schade",
    "machtsmisbruik",
    "ontwikkelingshulp",
    "vaarroute",
    "onveilig",
    "handelscorridor",
    "internationaal recht",
    "oorlog",
    "winst",
    "levensgevaarlijk",
    "gevaarlijk"
]

koopvaardij_bescherming = DiscourseConfiguration(
    title="Wet Bescherming Koopvaardij",
    description="Deze wetswijziging maakt het mogelijk dat particulieren geweld mogen gebruiken "
                "om schepen te beschermen tegen piraterij.",
    language="nl",
    topics=["piraat", "piraterij", "koopvaar"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
