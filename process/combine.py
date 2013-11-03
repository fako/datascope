from celery.result import AsyncResult

from HIF.process.base import Process
from HIF.input.http.google import GoogleImage
from HIF.input.http.wiki import WikiTranslate
from HIF.tasks import get_query_link, flatten_query_link, get_multi_query_link

class ImageTranslate(Process):
    # Classes to combine
    translate_model = WikiTranslate
    image_model = GoogleImage

    def process(self, *args, **kwargs):
        try:
            query = kwargs["query"]
        except KeyError:
            query = "cow"
        async_result = (get_query_link.s(query, self.translate_model ,"en","nl") | flatten_query_link.s("translation") | get_multi_query_link.s(self.image_model))()
        self.task = async_result.task_id

    def post_process(self, *args, **kwargs):
        task = AsyncResult(self.task_id)
        print task.parent.parent.result.results
        print task.result.results
