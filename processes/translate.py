from celery import group

from HIF.processes.core import Process, Retrieve
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate
from HIF.tasks import execute_process, flatten_process_results
from HIF.helpers.mixins import DataMixin


class ImageTranslate(Process, DataMixin):

    # HIF interface
    HIF_translate_model = "WikiTranslate"
    HIF_image_model = "GoogleImage"

    HIF_translations = {
        "query": "word",
        "results": "images"
    }


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
        image_config = {"_link": self.HIF_image_model}
        image_retriever = Retrieve()
        image_retriever.setup(**image_config)

        # Start Celery task
        task = (execute_process.s(query, translate_retriever.retain()) | flatten_process_results.s(key="translation") | execute_process.s(image_retriever.retain()))()
        self.task = task


    def post_process(self):
        self.rsl = self.data  # translates keys


    class Meta:
        proxy = True


#class ImageTranslations(GroupProcess):
#
#    def process(self):
#
#        # Get params
#        arg = self.args[0] # TODO: warn against improper usage
#        source_language = self.config.source_language
#        supported_languages = self.config._supported_languages
#        supported_languages.remove(source_language)
#
#        processes = []
#        for language in supported_languages:
#            # Setup config per language
#            configuration = self.config.dict(protected=True)
#            configuration.update({"translate_to": language})
#            # Add process to queue
#            process = ImageTranslate(configuration)
#            processes.append((arg,process.retain(),))
#
#        print "inside group process"
#        print processes
#
#        # Start a task that calls ImageTranslate processes with different translate_to config.
#        grp = group(execute_process.s(input,process) for input, process in processes).delay()
#        self.task = grp.id
#        self.retain()
#        return self.task
#
#    def post_process(self, *args, **kwargs):
#        data = self.data # data should contain list with process retain tuples
#        print "group post_process"
#        print(data)
#        results = []
#        for prc in data:
#            process = get_process_from_storage(prc)
#            if process.status == Status.DONE:
#                results += process.results
#            else:
#                return None
#
#        self.results = results
#        return self.results
#
#    class Meta:
#        proxy = True