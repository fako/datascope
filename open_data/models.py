from collections import OrderedDict

from core.models.organisms import Community, Individual


class DutchParliamentarySeatingTranscriptsCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("index", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.start_date", "$.end_date"],
                "_kwargs": {},
                "_resource": "OfficialAnnouncementsNetherlands",
                "_objective": {
                    "@": "soup.select('.lijst a')",
                    "link": "el.get('href')",
                    "title": "next(el.stripped_strings)",
                    "details": "el.em.get_text(strip=True)"
                },
                "_continuation_limit": 31,
            },
            "schema": {},
            "errors": {},
        }),
        ("documents", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@index",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.link"],
                "_kwargs": {},
                "_resource": "OfficialAnnouncementsDocumentNetherlands",
                "_objective": {
                    "@": "soup.find_all(class_='spreekbeurt')",
                    "#seating": "{key: value for key, value in zip(['year', 'number', 'date', 'published_at'], soup.find(class_='nummer').stripped_strings)}",
                    "speaker": "{" +
                        "'title': el.find(class_='voorvoegsels').get_text(strip=True) " +
                            "if el.find(class_='voorvoegsels') else ''," +
                        "'name': el.find(class_='achternaam').get_text(strip=True) " +
                            "if el.find(class_='achternaam') else ''," +
                        "'party': el.find(class_='politiek').get_text(strip=True) " +
                            "if el.find(class_='politiek') else ''" +
                    "}",
                    "paragraphs": "[paragraph.get_text(strip=True) for paragraph in el.find_all(class_='alineagroep')]"
                }
            },
            "schema": {},
            "errors": {},
        }),
    ])

    def finish_index(self, out, err):
        for document in out.individual_set.all().iterator():
            document["link"] = "https://zoek.officielebekendmakingen.nl" + document["link"]
            document.save()

    def initial_input(self, *args):
        return Individual.objects.create(
            community=self,
            properties={
                "start_date": args[0],
                "end_date": args[1]
            }
        )

    def set_kernel(self):
        self.kernel = self.current_growth.output

    class Meta:
        verbose_name = "Dutch parliamentary seating transcripts"
        verbose_name_plural = "Dutch parliamentary seating transcripts"
