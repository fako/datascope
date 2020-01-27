from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "doodstraf",
    "crimineel",
    "veroordeelde",
    "moordenaar",
    "bankier",
    "serie moordenaar",
    "pedofiel",
    "psychopaat",
    "onschuldige",
    "slachtoffer",
    "familie",
    "gevangenis",
    "openbaar ministerie",
    "rechter",
    "advocaat",
    "dodencel",
    "bewijs",
    "amnesty international",
    "getuige",
    "waarheid",
    "beul",
    "executie"
]

PLURAL_SUBJECTS = [
    "criminelen",
    "veroordeelden",
    "moordenaars",
    "bankiers"
    "serie moordenaars",
    "pedofielen",
    "psychopaten",
    "slachtoffers",
    "families",
    "gevangenisen",
    "rechters",
    "advocaten",
    "dodencellen",
    "bewijzen",
    "getuigen",
    "beulen",
    "executies"
]

DESCRIPTIVE_ADJECTIVES = [
    "ingeluist",
    "politiek",
    "onomkeerbaar",
    "onomkeerbare",
    "vastzitten",
    "beteren"
    "onbetrouwbaar",
    "onbetrouwbare",
    "vrijgekomen",
    "recidive",
    "recidiverisico",
    "recidivepreventie",
    "dure",
    "vergissing",
    "vervalst",
    "corrupte",
    "onvolledige",
    "onverbeterlijke",
    "ongeneeslijke",
    "hopeloze",
    "gevaarlijke",
    "gebrekkig",
    "wrede",
    "gevoelloze",
    "voortdurende",
    "genoegdoening",
    "oog om oog",
    "wraak",
    "zorgvuldig",
    "onzorgvuldig",
    "eerlijk",
    "oneerlijk",
    "aanvullend",
    "repressie",
    "preventie",
    "mensenrechten",
    "rechten van de mens",
    "harde aanpak",
]

doodstraf = DiscourseConfiguration(
    title="Doodstraf",
    description="De doodstraf bestaat al heel lang niet in Nederland en er zijn geen plannen hem in te voeren. "
                "Toch zijn er mensen die voor de doodstraf pleiten.",
    language="nl",
    topics=["doodstraf"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
