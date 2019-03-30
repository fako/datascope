from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "mijnbouwer",
    "baggeraar",
    "wetenschapper",
    "International Seabed Authority",
    "ISA",
    "DEME",
    "NIOZ",
    "Nederlands Instituut voor Onderzoek der Zee",
    "universiteit",
    "Netherlands Initiative Changing Oceans",
    "NICO",
    "JPI Oceans",
    "Verenigde naties",
    "Milieu defensie",
    "Greenpeace",
    "National Oceanic and Atmospheric Administration",
    "NOAA",
    "Europese Commissie",
    "internationaal recht",
    "verdragen"
]

PLURAL_SUBJECTS = [
    "mijnbouwers",
    "baggeraars",
    "wetenschappers",
    "universiteiten",
    "biologen",
    "geologen",
    "oceanologen",
]

DESCRIPTIVE_ADJECTIVES = [
    "diepzee",
    "mijnbouw",
    "geld verdienen",
    "onderzoek",
    "grondstoffen",
    "energie",
    "reserves",
    "strategisch",
    "werkgelegenheid",
    "welvaart",
    "economie",
    "schaarste",
    "rechtmatig",
    "voor iedereen",
    "milieu",
    "zeeleven",
    "vissen",
    "duurzaamheid",
    "verstoring",
    "vernietiging",
    "zuurstof tekort",
    "atmosfeer",
    "verdrag",
    "mijnbouw code",
    "werelderfgoed",
    "onrechtmatig",
    "corrupt",
    "biosfeer",
    "methaan",
    "klimaatverandering",
    "energievoorziening",
    "natuurbehoud",
    "ecologie",
    "zeebodem",
    "oceaan"
]

diepzee_mijnbouw = DiscourseConfiguration(
    title="Diepzee Mijnbouw",
    description="Er liggen waardevolle grondstoffen op de zeebodem, "
                "maar het mijnen van deze grondstoffen zou ten koste kunnen gaan van onze oceanen",
    language="nl",
    topics=["diepzee", "mijnbouw"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
