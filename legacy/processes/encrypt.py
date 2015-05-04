from random import shuffle


CHARS = "acegikmoqsuwy"
l = list(CHARS)
shuffle(l)
CRYPTS = "".join(l)
ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def encrypt_char(char):

    if not str.isalpha(char) or char not in CHARS:
        return char

    if str.isupper(char):
        char = char.lower()
        to_upper = True
    else:
        to_upper = False

    pos = CHARS.find(char)
    return CRYPTS[pos]


def decrypt_char(char):
    if not str.isalpha(char) or char not in CHARS:
        return char

    if str.isupper(char):
        char = char.lower()
        to_upper = True
    else:
        to_upper = False

    pos = CRYPTS.find(char)
    return CHARS[pos]


def print_key():
    for c in ALPHABET:
        print encrypt_char(c) + ' = ' + c

TEXT = """
Psst, hier ben ik

Ik denk dat we met meer voorzichtigheid te werk moeten gaan
The Big Green bevind zich tenslotte ook in Falkrest
Misschien heeft Markelhay helemaal niet de touwtjes in handen in Falkrest
Dat is mijns inziens zeker een mogelijkheid

Ik heb van Morgi begrepen dat hij deze draak mogelijk ooit eerder is tegengekomen
En dat de draak wellicht plannen heeft voor het maken van een Dracolich via de Cult of Dragons
Wat heeft het voor zin om Falkrest uit te persen als er een Dracolich in Chondathan vliegt?

Graag jullie mening

Groet,

Rat
"""
ENCRYPTED = ""
for char in TEXT:
    ENCRYPTED += encrypt_char(char)

print ENCRYPTED
print print_key()
