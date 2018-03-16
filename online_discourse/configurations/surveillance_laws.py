measures = [
    "bestrijden",
    "tegengaan",
    "stoppen",
    "bestrijding"
]
services = [
    "inlichtingen ",
    "opsporings ",
    "opsporings",
    "geheime "
]
innocent = [
    "onschuldige ",
    "weerloze ",
    "machteloze ",
    "trouwhartige ",
    "getrouwe ",
    "eerlijke "
]


SINGULAR_SUBJECTS = [
    "privacy",
    "dreigingsniveau",

    "sleepnet wet",
    "aftapwet",
    "wet op de inlichtingen en veiligheidsdiensten",
    "inlichtingenwet",

    *[service + "dienst" for service in services],
    "terrorist",
    *["terrorisme " + measure for measure in measures],
    "crimineel",
    *["criminaliteit " + measure for measure in measures],
    "burger",
    *[adj + "burger" for adj in innocent],
    "persoon",
    *[adj + "persoon" for adj in innocent],

    "onafhankelijke commissie",
    "de staat",
    "de overheid",
    "van binnenlandse zaken",
    "van BZ",
    "buitenland",

    "syrische strijder",
    "cyberwarfare",
    "bevolkingsgroep",
    "minderheid",
]

PLURAL_SUBJECTS = [
    *[service + "dienst" for service in services],
    "terroristen",
    *["terrorisme " + measure for measure in measures],
    "criminelen",
    *["criminaliteit " + measure for measure in measures],
    "burgers",
    *[adj + "burgers" for adj in innocent],
    "personen",
    *[adj + "personen" for adj in innocent],
    "syrische strijder",
    "bevolkingsgroep",
    "minderheden",
]

DESCRIPTIVE_ADJECTIVES = [
    "inlichtingen",
    "informatie",
    "data",
    "opslag",
    "bewaren",
    "verzamelen",
    "inwinnen",
    "kabel",
    "ether",
    "onderscheppen van *",

    "misbruik",
    "controle",
    "ongericht",
    "schending",
    "big brother",
    "surveillance",
    "onschuldig",
    "onschuldpresumptie",
    "gevaarlijk",
    "risico",
    "veiligheid",
    "persoonlijk",
    "mensenlevens",

    "toestemming",
    "toetsing",
    "betrouwbaar",
    "macht",
    "bescherming",
    "handhaving",
    "tot het tegendeel bewezen is",
    "uitgebreide bevoegdheden",

    "genocide",
    "dictator",
    "onderdrukking",
    "discriminatie",
    "penopticum",
    "terroristische",
    "criminele",
]
