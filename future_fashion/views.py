from __future__ import unicode_literals, absolute_import, print_function, division

from itertools import islice

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from core.views.community import HtmlCommunityView


class FutureFashionHtmlView(HtmlCommunityView):

    def get(self, request, community_class, path=None, *args, **kwargs):
        if not "$reference" in request.GET:
            community = community_class.objects.last()
            results = []
            for ind in community.kernel.individual_set.all()[:10]:
                ind.properties["id"] = ind.id
                results.append(ind.properties)
            return render_to_response(
                "{}/{}".format(community_class.get_name(), HtmlCommunityView.OK),
                {
                    'response': {
                        'results': results
                    }
                },
                request
            )
        return super(FutureFashionHtmlView, self).get(request, community_class, path=path, *args, **kwargs)
