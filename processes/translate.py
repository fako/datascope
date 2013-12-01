from celery import group

from HIF.processes.core import Process, Retrieve, GroupProcess
from HIF.tasks import execute_process, flatten_process_results
from HIF.helpers.mixins import DataMixin


class ImageTranslate(Process, DataMixin):

    # HIF interface
    HIF_translate_model = "WikiTranslate"  # HIF.input.http.wiki
    HIF_image_model = "GoogleImage"  # HIF.input.http.google

    HIF_translations = {
        "query": "word",
        "results": "images"
    }
    HIF_child_process = 'Retrieve'


    @property
    def data_source(self):
        source = self.subs["Retrieve"][0]
        source.setup()
        return source.results


    def process(self):
        # Get params
        query = self.config.query
        translate_to = self.args[0] or self.config.translate_to

        # Setup translate retriever
        translate_config = {
            "_link": self.HIF_translate_model,
            "translate_to": translate_to
        }
        translate_config.update(self.config.dict())
        translate_retriever = Retrieve()
        translate_retriever.setup(**translate_config)
        # Setup image retriever
        image_config = {"_link": self.HIF_image_model, "_context":"{}+{}".format(query, translate_to)}
        image_retriever = Retrieve()
        image_retriever.setup(**image_config)

        # Start Celery task
        task = (execute_process.s(query, translate_retriever.retain()) | flatten_process_results.s(key="translation") | execute_process.s(image_retriever.retain()))()
        self.task = task


    def post_process(self):
        self.rsl = self.data  # translates keys


    class Meta:
        app_label = "HIF"
        proxy = True


class ImageTranslations(GroupProcess):

    HIF_child_process = 'ImageTranslate'

    def setup(self, *args, **kwargs):
        kwargs["_process"] = 'ImageTranslate'  # move to core?
        super(ImageTranslations, self).setup(*args, **kwargs)
        self.args = self.config._supported_languages
        source_language = self.config.source_language
        if source_language in self.args:
            self.args.remove(source_language)
        self.save()


    def post_process(self, *args, **kwargs):
        # TODO: This could also be done by translating the results from GroupProcess, no need to write it out every time ...
        results = []
        for language, data in zip(self.args, self.data):
            results.append({
                "language": language,
                "translations": data
            })
        self.rsl = results


    class Meta:
        app_label = "HIF"
        proxy = True