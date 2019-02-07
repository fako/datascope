from copy import copy

from core.models.resources.http import HttpResource


class ComplexityAnalysis(HttpResource):

    URI_TEMPLATE = "https://api.wizenoze.com/v2/complexity/url?targetAudienceId=31"

    HEADERS = {
        "Content-Type": "application/json"
    }

    CONFIG_NAMESPACE = "wizenoze"

    # TODO: validate that kwargs match necessary body (especially the url kwarg)
    """
    TODO: this resource requires a POST, but it takes one static argument "languageCode".
    This argument should come from config or somewhere else,
    because as kwargs to post() does not work well with the pipeline below:

    ("wizenoze", {
        "process": "HttpResourceProcessor.submit_mass",
        "input": "@search",
        "contribute": "Update:ExtractProcessor.extract_from_resource",
        "output": "@search",
        "config": {
            "_args": [],
            "_kwargs": {
                "url": "$.url",
                "languageCode": "en"
            },
            "_resource": "ComplexityAnalysis",
            "_objective": {
                "@": "$",
                "url": "$.metadata.url",
                "audience": "$.classification.audience",
                "document": "$.contentMetadata.documentStats",
                "audience_probabilities": "$.complexity.audienceProbabilities"
            },
            "_update_key": "url"
        },
        "schema": {},
        "errors": {},
    })
    """

    def headers(self):
        headers = copy(self.HEADERS)
        headers["Authorization"] = self.config.api_key
        return headers

    @property
    def content(self):
        content_type, json = super().content
        # Adding the used URL to the response, because that's usually needed to do data updates
        if json.get("metadata"):
            json["metadata"]["url"] = self.request["json"]["url"]
        return content_type, [json]  # putting results in list to facilitate data updates

    class Meta:
        verbose_name = "Complexity analysis"
        verbose_name_plural = "Complexity analyses"
