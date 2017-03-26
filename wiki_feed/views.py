from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.conf import settings

from rest_framework import status

from core.views import CommunityView
from wiki_feed.models import WikiFeedPublishCommunity


def wiki_page_update(request, page):
    signature = WikiFeedPublishCommunity.get_signature_from_input(*page.split("/"), **request.GET.dict())
    WikiFeedPublishCommunity.objects.filter(signature=signature).delete()
    response = CommunityView().get_response(WikiFeedPublishCommunity, page, request.GET.dict())
    if response.status_code == status.HTTP_202_ACCEPTED:
        wait_url = reverse("v1:wiki_page_wait", kwargs={"page": page})
        wait_query = request.META.get("QUERY_STRING")
        return redirect("{}?{}".format(wait_url, wait_query))
    return redirect("https://en.wikipedia.org/wiki/{}".format(page))


def wiki_page_wait(request, page):
    return render_to_response("wiki_feed/wait.html", {
        "segments_to_service": settings.SEGMENTS_TO_SERVICE,
        "service_query": page,
        "continue_path": "https://en.wikipedia.org/wiki/{}".format(page),
        "page_title": page
    })
