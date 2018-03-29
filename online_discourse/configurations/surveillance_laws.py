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
    "terrorist",
    "crimineel",
    "burger",
    "persoon",

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

] + \
[service + "dienst" for service in services] + \
["terrorisme " + measure for measure in measures] + \
["criminaliteit " + measure for measure in measures] + \
[adj + "burger" for adj in innocent] + \
[adj + "persoon" for adj in innocent]

PLURAL_SUBJECTS = [
    "terroristen",
    "criminelen",
    "burgers",
    "personen",
    "syrische strijder",
    "bevolkingsgroep",
    "minderheden",
] + \
[service + "dienst" for service in services] + \
["terrorisme " + measure for measure in measures] + \
["criminaliteit " + measure for measure in measures] + \
[adj + "burgers" for adj in innocent] + \
[adj + "personen" for adj in innocent]

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
