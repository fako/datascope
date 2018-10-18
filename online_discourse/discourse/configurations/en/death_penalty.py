from online_discourse.discourse import DiscourseConfiguration


SINGULAR_SUBJECTS = [
    "death penalty",
    "death sentence",
    "criminal",
    "convicted",
    "murderer",
    "killer",
    "banker",
    "serial killer",
    "pedophile",
    "psychopath",
    "innocence"
    "victim",
    "family",
    "prison",
    "jail",
    "public prosecutor",
    "public attorney",
    "judge",
    "lawyer",
    "death row",
    "death cell",
    "proof",
    "amnesty international",
    "witness",
    "truth",
    "executioner",
    "execution"
]

PLURAL_SUBJECTS = [
    "criminals",
    "murderers",
    "killers",
    "bankers"
    "serial killers",
    "pedophiles",
    "psychopaths",
    "victims",
    "families",
    "prisons",
    "jails",
    "judges",
    "lawyers",
    "proofs",
    "witnesses",
    "executioners",
    "executions"
]

DESCRIPTIVE_ADJECTIVES = [
    "innocent",
    "framed",
    "political",
    "irreversible",
    "imprisoned",
    "better one's life"
    "unreliable",
    "untrustworthy",
    "get free",
    "recidivism",
    "recidivism risk",
    "recidivism reduction",
    "expansive",
    "mistake",
    "falsified",
    "corrupt",
    "incomplete",
    "incorrigible",
    "unredeemable",
    "incurable",
    "hopeless",
    "dangerous",
    "lacking",
    "cruel",
    "insensitive",
    "constant",
    "satisfaction",
    "eye for an eye",
    "revenge",
    "careful",
    "sloppy",
    "honest",
    "dishonest",
    "additional",
    "repression",
    "prevention",
    "human rights",
    "hard approach",
]

death_penalty = DiscourseConfiguration(
    title="Death Penalty",
    description="America is one of the few Western countries upholding the death penalty. " + \
                "There is a constant debate about whether the death penalty should get abolished.",
    language="en",
    singular_subjects=SINGULAR_SUBJECTS,
    plural_subjects=PLURAL_SUBJECTS,
    descriptive_adjectives=DESCRIPTIVE_ADJECTIVES
)
