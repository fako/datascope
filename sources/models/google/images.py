from __future__ import unicode_literals, absolute_import, print_function, division

from sources.models.google.query import GoogleQuery


class GoogleImage(GoogleQuery):

    URI_TEMPLATE = 'https://www.googleapis.com/customsearch/v1?{}="{}"'
    PARAMETERS = {
        'searchType':'image',
    }
    # HIF_objective = {
    #     "link": None,
    #     "image.width": None,
    #     "image.height": None,
    #     "image.thumbnailLink": None
    # }
    # HIF_translations = {
    #     "image.width": "width",
    #     "image.height": "height",
    #     "image.thumbnailLink": "thumbnailLink"
    # }

    def auth_parameters(self):
        params = super(GoogleImage, self).auth_parameters()
        params.update({
            "cx": self.config.cx
        })
        return params
