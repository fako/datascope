from celery import group

from HIF.processes.core import AsyncProcess, GroupProcess, Status
from HIF.processes.retrieve import Retrieve
from HIF.helpers.storage import get_process_from_storage
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate
from HIF.tasks import execute_process, flatten_process_results


class ImageTranslate(AsyncProcess):

    # HIF interface
    _translate_model = WikiTranslate
    _image_model = GoogleImage

    def process(self):
        # Get params
        query = self.args[0] # TODO: warn against improper usage

        # Setup retrievers
        translate_config = {"_link": self._translate_model}
        translate_config.update(self.config.dict())
        translate_retriever = Retrieve(translate_config)
        image_retriever_group = GroupProcess({
            "_process": Retrieve,
            "_link": self._image_model,
            "_argument_key": "word",
            "_result_key": "images",
        })

        # Start Celery task
        self.retain()
        async_result = (execute_process.s(query, translate_retriever.retain()) | flatten_process_results.s(key="translation") | execute_process.s(image_retriever_group.retain()))()
        self.task = async_result.task_id
        self.save()
        return self.task

    def post_process(self, *args, **kwargs):
        data = self.data
        subprocess = get_process_from_storage(data)
        results = None
        if subprocess.status == Status.DONE:
            results = [{
                "language": self.config.translate_to,
                "results": subprocess.results
            }]
        self.results = results
        return self.results

    class Meta:
        proxy = True


class ImageTranslations(GroupProcess):

    def process(self):

        # Get params
        arg = self.args[0] # TODO: warn against improper usage
        source_language = self.config.source_language
        supported_languages = self.config._supported_languages
        supported_languages.remove(source_language)

        processes = []
        for language in supported_languages:
            # Setup config per language
            configuration = self.config.dict(protected=True)
            configuration.update({"translate_to": language})
            # Add process to queue
            process = ImageTranslate(configuration)
            processes.append((arg,process.retain(),))

        print "inside group process"
        print processes

        # Start a task that calls ImageTranslate processes with different translate_to config.
        grp = group(execute_process.s(input,process) for input, process in processes).delay()
        self.task = grp.id
        self.retain()
        return self.task

    def post_process(self, *args, **kwargs):
        data = self.data # data should contain list with process retain tuples
        print "group post_process"
        print(data)
        results = []
        for prc in data:
            process = get_process_from_storage(prc)
            if process.status == Status.DONE:
                results += process.results
            else:
                return None

        self.results = results
        return self.results

    class Meta:
        proxy = True