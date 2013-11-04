from celery.result import AsyncResult

from HIF.processes.core import Process
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate
from HIF.tasks import retrieve_link, flatten_process_results, retrieve_multi_query_link

class ImageTranslate(Process):
    # Classes to combine
    translate_model = WikiTranslate
    image_model = GoogleImage

    def process(self, *args, **kwargs):
        try:
            query = kwargs["query"]
        except KeyError:
            query = "cow"
        async_result = (retrieve_link.s(self.translate_model, source_language="en", translate_to="nl", query=query) | flatten_process_results.s("translation") | retrieve_multi_query_link.s(self.image_model))()
        self.task = async_result.task_id

    def post_process(self, *args, **kwargs):
        task = AsyncResult(self.task)
        return task
        #print task.parent.parent.result.results
        #print task.result.results
