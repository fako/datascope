from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import BrowserResource


class GoogleTranslate(BrowserResource):

    URI_TEMPLATE = "https://translate.google.nl/#{}/{}/{}"

    @property
    def success(self):
        return self.status == 1