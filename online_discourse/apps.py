from django.apps import AppConfig

from datagrowth.configuration import register_defaults


class OnlineDiscourseConfig(AppConfig):
    name = 'online_discourse'
    verbose_name = "Online Discourse"

    def ready(self):
        register_defaults("discourse_download", {
            "url_key": "url",
            "resource_key": "resource"
        })
