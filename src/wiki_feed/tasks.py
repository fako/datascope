from django.core.management import call_command
from celery import current_app as app


@app.task(name="wiki_feed.update_wiki_feed")
def update_wiki_feed():
    call_command("grow_wiki_feed", delete=True)
    call_command("publish_wiki_feed", delete=True)
