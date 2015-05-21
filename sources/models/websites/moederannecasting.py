import re
import urllib

import requests

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.resources.http import HttpResource
from core.utils import configuration


class MoederAnneCastingSession(HttpResource):

    URI_TEMPLATE = "http://zoekbestand.moederannecasting.nl/atlantispubliek/Resultaten.aspx"
    GET_SCHEMA = {
        "args": None,
        "kwargs": None
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
        "Content-Type":	"application/x-www-form-urlencoded"
    }

    config = configuration.ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION,
        namespace="moeder_anne_casting"
    )

    def data(self):
        data_dict = {
            "invalshoek": 71,
            "segmenten": "",
            "highlightclassname": "highlight",
            "eenvoudig_zoeken": "false",
            "aantalperpagina": 12,
            "uitgebreid_zoeken": "true",
            "URL_XSLTSERVICE": "http://zoekbestand.moederannecasting.nl/AtlantisPubliek/XSLTService.asmx",
            "uzoeken": "true",
            "vorigezoekvraag": "",
            "cmveldValue_Naam": "",
            "cmveldName_Naam": "Naam",
            "cmveldFilter_Naam": "",
            "cmveldValue_Geslacht": "",
            "cmveldnaam": "Geslacht",
            "beschrijvingssoortenids":72,
            "cmveldFilter_Geslacht": "gelijkaan",
            "cmveldHighlight_Geslacht": "off",
            "cmveldName_Geslacht": "Geslacht",
            "cmveldValue_Leeftijd_van":"22/5/1914",
            "cmveldValue_Leeftijd_tot": "21/5/2015",
            "cmveldName_Leeftijd_van": "Leeftijd_van",
            "cmveldName_Leeftijd_tot": "Leeftijd_tot",
            "cmveldFilter_Leeftijd_van": "",
            "cmveldFilter_Leeftijd_tot": "",
            "cmveldValue_SpecifiekXXzoekwoord": "",
            "cmveldFilter_SpecifiekXXzoekwoord":"gelijkaan",
            "cmveldHighlight_SpecifiekXXzoekwoord": "off",
            "cmveldName_SpecifiekXXzoekwoord": "SpecifiekXXzoekwoord",
            "cmveldValue_Imfnr": "",
            "cmveldName_Imfnr": "Imfnr",
            "cmveldFilter_Imfnr": "gelijkaan",
            "cmveldValue_Lengte_van": "",
            "cmveldValue_Lengte_tot": "",
            "cmveldName_Lengte_van": "Lengte_van",
            "cmveldName_Lengte_tot": "Lengte_tot",
            "cmveldFilter_Lengte_van": "",
            "cmveldFilter_Lengte_tot": "",
            "cmveldValue_Confectiemaat": "",
            "cmveldFilter_Confectiemaat": "gelijkaan",
            "cmveldHighlight_Confectiemaat": "off",
            "cmveldName_Confectiemaat": "Confectiemaat",
            "cmveldValue_KleurXXogen": "",
            "cmveldFilter_KleurXXogen": "gelijkaan",
            "cmveldHighlight_KleurXXogen": "off",
            "cmveldName_KleurXXogen": "KleurXXogen",
            "cmveldValue_KleurXXhaar": "",
            "cmveldFilter_KleurXXhaar": "gelijkaan",
            "cmveldHighlight_KleurXXhaar": "off",
            "cmveldName_KleurXXhaar": "KleurXXhaar"
        }
        data = data_dict.items()
        cmveldnamen = ["Geslacht", "SpecifiekXXzoekwoord", "Confectiemaat", "KleurXXogen", "KleurXXhaar"]
        for name in cmveldnamen:
            data.append(("cmveldnaam", name,))
            data.append(("beschrijvingssoortenids", 72,))
        return urllib.urlencode(data)


class MoederAnneCastingSearch(HttpResource):

    URI_TEMPLATE = "http://zoekbestand.moederannecasting.nl/atlantispubliek/Resultaten.aspx"
    GET_SCHEMA = {
        "args": None,
        "kwargs": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "maximum": 620
                }
            }
        }
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
        "Content-Type":	"application/x-www-form-urlencoded"
    }

    config = configuration.ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION,
        namespace="moeder_anne_casting"
    )

    def get(self, *args, **kwargs):
        if self.session is None or not self.session.cookies.get("ASP.NET_SessionId"):
            link = MoederAnneCastingSession()
            link.session = requests.Session()
            link.get()
            self.session = link.session
        return super(MoederAnneCastingSearch, self).get(*args, **kwargs)

    def data(self, **kwargs):
        return {
            "globaal": "",
            "view": "",
            "invalshoek": 71,
            "mode": "uitgebreid",
            "volgnummer": 0,
            "aantalperpagina": 12,
            "huidigepagina": kwargs.get("page"),
            "url_icoonhttphandler": "http://zoekbestand.moederannecasting.nl/HttpHandler/icoon.ico",
            "schikking": "",
            "sortering": "",
            "gekoppeld_globaal": "",
            "gekoppeld_uitgebreid_zoeken": "",
            "gekoppeld_mode": "",
            "gekoppeld_volgnummer": "",
            "URL_WINKELWAGEN": "",
            "URL_XSLTSERVICE": "http://zoekbestand.moederannecasting.nl/AtlantisPubliek/XSLTService.asmx"
        }

