import json

from django.core.management.base import BaseCommand

from core.helpers.storage import get_hif_model
from core.helpers.enums import ProcessStatus

import requests
import re


def findParagraph(wholeText,term):
    #find = re.compile(r'^(.*?)\..*')
    #m = re.match(find, wholeText)
    #print m.group(1)
    text = re.sub(r'\<ref.*?ref\>',"", wholeText)
    paragraphlist = re.split(r"\n\n", text)

    correctPara = ""
    for s in paragraphlist:
        if(re.search(term,s)):
            correctPara = s
            break

    brackettext = re.findall(r'\[.*?\]\]', correctPara)
    for b in brackettext:
        items = re.split(r'\|',b)
        first = re.sub(r'[\[\]]',"",items[0])
        correctPara = re.sub(r'\[.*?\]\]',first,correctPara, count = 1)
    return correctPara


def splitParagraphIntoSentences(paragraph):
    sentenceEnders = re.compile(r"""
        # Split sentences on whitespace between them.
        (?:               # Group for two positive lookbehinds.
        (?<=[.!?])      # Either an end of sentence punct,
        | (?<=[.!?]['"])  # or end of sentence punct and quote.
        )                 # End group of two positive lookbehinds.
        (?<!  Mr\.   )    # Don't end sentence on "Mr."
        (?<!  Mrs\.  )    # Don't end sentence on "Mrs."
        (?<!  St\.  )    # Don't end sentence on "St."
        (?<!  \s[A-Z]\.  )    # Don't end sentence on " [LETTER]."
        (?<!  Jr\.   )    # Don't end sentence on "Jr."
        (?<!  Dr\.   )    # Don't end sentence on "Dr."
        (?<!  Prof\. )    # Don't end sentence on "Prof."
        (?<!  Sr\.   )    # Don't end sentence on "Sr."
        (?<!  dir\.   )    # Don't end sentence on "Dir."
        \s+               # Split on whitespace between sentences.
        """,
        re.IGNORECASE | re.VERBOSE)
    sentenceList = sentenceEnders.split(paragraph)
    return sentenceList


class Command(BaseCommand):
    """
    Clears TextStorage and/or ProcessStorage from the database.
    """

    def handle(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        self.args = "<city_name>/<lat>|<lon> <city_name>/<lat>|<lon> ..."

        # Import models here to prevent circular imports
        from core.input.http.wiki import WikiBaseQuery
        from core.processes.base import Retrieve
        from core.output.http.services.manifests import CityCelebritiesService
        import hashlib


        if not args:
            print("You'll need to specify coordinates like: London/51.5286416|-0.1015987")
            return

        for arg in args:

            # Start the process
            city, coords = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords))
            city_celebrities = CityCelebritiesService()
            city_celebrities.setup(query=unicode(city))

            wbq = WikiBaseQuery()
            wbq.get("|".join([page['title'] for page in city_celebrities.content]))

            new_locations = []
            for location in city_celebrities.content:

                new_persons = []
                for person in location['people']:
                    r = requests.get(u'http://en.wikipedia.org/wiki/{}?action=raw'.format(person['title'].replace(' ', '_')))
                    searchTerm = location['title']
                    #print r.text
                    paragraph = findParagraph(r.text, searchTerm)
                    sentences = splitParagraphIntoSentences(paragraph)
                    #print sentences
                    mylist = []
                    for s in sentences:
                        mylist.append(s.strip())
                    for count, i in enumerate(mylist):
                        temp_str = ''
                        #print i
                        if (re.search(searchTerm, i)):
                            #print "MATCH"
                            if (count < (len(mylist)-1)):
                                temp_str = mylist[count+1]
                            else:
                                temp_str = mylist[0]

                            break
                    if len(temp_str) <= 200 and temp_str:
                        person['text'] = temp_str
                        new_persons.append(person)

                if len(new_persons):
                    location['people'] = new_persons
                    new_locations.append(location)

            city_celebrities.content = new_locations
            city_celebrities.save()
