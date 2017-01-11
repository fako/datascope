from datetime import date

from core.models.resources.http import HttpResource


class WikipediaPageviewDetails(HttpResource):

    URI_TEMPLATE = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{}/all-access/user/{}/daily/{}/{}"
    CONFIG_NAMESPACE = "wikipedia"

    def send(self, method, *args, **kwargs):
        start_date = self.config.start_time.strftime("%Y%m%d")
        end_date = self.config.end_time.strftime("%Y%m%d")
        args = (self.config.wiki_domain, args[0], start_date, end_date)
        return super(WikipediaPageviewDetails, self).send(method, *args, **kwargs)
