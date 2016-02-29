import re
import requests

from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template.loader import render_to_string

from rest_framework import status

from core.views import CommunityView
from wiki_news.models import WikiNewsCommunity


TARGET_WIKI = "https://wikitech.wikimedia.org/"


def edit_wiki(page, content):
    wiki_session = requests.Session()
    api_endpoint = TARGET_WIKI + "w/api.php"
    initial_login_payload = {
        'action': 'query',
        'format': 'json',
        'utf8': '',
        'meta': 'tokens',
        'type': 'login'
    }
    response = wiki_session.post(api_endpoint, data=initial_login_payload)
    login_token = response.json()['query']['tokens']['logintoken']
    confirm_login_payload = {
        'action': 'login',
        'format': 'json',
        'utf8': '',
        'lgname': 'Fako85',
        'lgpassword': '1Wiki0110&0010',
        'lgtoken': login_token
    }
    wiki_session.post(api_endpoint, data=confirm_login_payload)
    edit_token_params = {
        'action': 'query',
        'format': 'json',
        'meta': 'tokens',
    }
    response = wiki_session.get(api_endpoint, params=edit_token_params)
    edit_token = response.json()['query']['tokens']['csrftoken']
    edit_payload = {
        'action': 'edit',
        'assert': 'user',
        'format': 'json',
        'utf8': '',
        'text': content,
        'title': page,
        'nocreate': 1,
        'token': edit_token
    }
    return wiki_session.post(api_endpoint, edit_payload)


def get_existing_sections(page):
    page_url = "{}wiki/{}".format(TARGET_WIKI, page)

    page_response = requests.get(page_url, params={"action": "raw"})
    anchor_regex = re.compile("\{\{\s*anchor\s*\|([^}]+)")
    current_anchor = None
    sections = {
        "header": []
    }
    for line in page_response.text.splitlines():
        match = anchor_regex.match(line)
        if match:
            current_anchor = match.groups()[0].strip()
            sections[current_anchor] = []
        elif match is None and current_anchor:
            sections[current_anchor].append(line)
        else:
            sections["header"].append(line)
    return sections


def wiki_page_update(request, page):
    response = CommunityView().get_service_data_response(WikiNewsCommunity, "latest-news", request.GET.dict())
    if response.status_code == status.HTTP_202_ACCEPTED:
        return redirect("v1:wiki_page_wait", page)
    existing_sections = get_existing_sections(page)
    content = "\n".join(existing_sections["header"])
    for page_details in response.data["results"]:
        if page_details["pageid"] in existing_sections:
            content += "\n".join(existing_sections[page_details["pageid"]])
        else:
            content += render_to_string("wiki_news/section.wml", {"page": page_details})

    # edit = edit_wiki(page, "NEWEST! E-MAZING!")
    # out = HttpResponse(edit.json())
    # out["content-type"] = "application/json"
    # return out
    return HttpResponse("testing")


def wiki_page_wait(request, page):
    # Renders a template that redirects to wiki_page_update when results are in
    return HttpResponse(page)


def wiki_page_details(request):
    pass
