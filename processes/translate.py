from celery.result import AsyncResult, GroupResult
from celery import group

from HIF.processes.core import AsyncProcess, GroupProcess
from HIF.processes.retrieve import Retrieve
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate
from HIF.tasks import execute_process, flatten_process_results


class ImageTranslate(AsyncProcess):

    # HIF interface
    _translate_model = WikiTranslate
    _image_model = GoogleImage

    def process(self):
        # Get params
        query = self.args[0]

        # Setup retrievers
        translate_config = {"_link": self._translate_model}
        translate_config.update(self.config.dict())
        translate_retriever = Retrieve(translate_config)
        image_retriever_group = GroupProcess({
            "_process": Retrieve,
            "_link": self._image_model,
        })

        # Start Celery task
        self.retain()
        async_result = (execute_process.s(query, translate_retriever.retain()) | flatten_process_results.s(key="translation") | execute_process.s(image_retriever_group.retain()))()
        self.task = async_result.task_id
        self.save()
        return self.task

    def post_process(self, *args, **kwargs):
        # fetch process and work with it!!
        self.results = [{
            "language": self.config.translate_to,
            "results": self.data.result
        }]
        return self.results

    class Meta:
        proxy = True


class ImageMultiTranslate(AsyncProcess):

    _config = ["supported_languages"]
    _config_namespace = "HIF"

    def process(self):
        # Get params
        query = self.kwargs["query"]
        source_language = self.kwargs["source_language"]
        supported_languages = self.config.supported_languages
        supported_languages.remove(source_language)

        # Start Celery
        self.save()
        async_result = execute_process.delay((supported_languages, self.id,), ImageTranslate, "translate_to", query=query, source_language=source_language)
        self.task = async_result.task_id
        self.save()

    def post_process(self, *args, **kwargs):
        task = AsyncResult(self.task)
        rsl, trash = task.result
        self.results = rsl
        return self.results

    class Meta:
        proxy = True