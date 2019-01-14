from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "energie",
    "biomassa",
    "co2",
    "atmosfeer",
    "bos",
    "organisme",
    "koolstofdioxide",
    "bosbeheer",
    "brandstof",
    "kolencentrale",
    "plant",
    "koolstof",
    "steenkool",
    "productiebos",
    "biobased economy",
    "afvalhout",
    "biodiversiteit",
    "landbouw",
    "toekomst",
    "koolstofschuld",
    "boseigenaar",
    "tak",
    "koolstofcyclus",
    "overheid",
    "biotechnologie",
    "aardgas",
    "snoeiafval",
    "bosbouw",
    "ecoloog",
    "europa",
    "tophout",
    "landbouwgrond"
]

PLURAL_SUBJECTS = [
    "bossen",
    "organismen",
    "brandstoffen",
    "kolencentrales",
    "takhout",
    "planten",
    "koolstoffen",
    "steenkolen",
    "productiebossen",
    "boseigenaren"
    "takken",
    "houtpellets",
    "korrels",
    "broeikasgassen",
    "ecologen",
    "energietransitie",
    "energievoorziening",
    "bedrijfsleven",
    "plantenresten",
    "houtzagerijen"
]

DESCRIPTIVE_ADJECTIVES = [
    "duurzame",
    "bijstook",
    "beschermen",
    "verbranding",
    "bijgestookt",
    "opgewekt"
    "fossiele",
    "houtachtige",
    "stimulering",
    "onttrekken",
    "groeien",
    "groene",
    "netto",
    "verbrandt",
    "micro",
    "omgehakt",
    "gesubsidieerd",
    "geld",
    "geperste",
    "oogsten",
    "ontbossing",
    "petrochemische",
    "aangroeien",
    "klimaatneutrale",
    "greenwashing",
    "ecosysteemfunctie",
    "ecologisch",
    "bioraffinage",
    "duurzaamheidscriteria",
    "duurzaaamheidscertificaten",
    "duurzaamheidsclaims",
    "energiedichtheid",
    "koolstofbalans",
    "bio",
]

biomassa = DiscourseConfiguration(
    title="Biomassa",
    description="Er bestaat in Nederland weinig twijfel over dat klimaatverandering een probleem is. "
                "Hoe dit probleem moet worden opgelost staat wel ter discussie. "
                "Vooral biomassa is omstreden.",
    language="nl",
    topics=["biomassa"],
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
