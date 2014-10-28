from core.processes.base import Process, Retrieve, GroupProcess
from core.tasks import execute_process, extend_process


class VisualTranslation(Process):

    # HIF interface
    HIF_translate_model = "WikiTranslate"  # core.input.http.wiki
    HIF_image_model = "GoogleImage"  # core.input.http.google
    HIF_video_model = "YouTubeSearch"  # core.input.http.google

    def process(self):
        # Get params
        query = self.config.query
        translate_to = self.config.translate_to

        # Setup translate retriever
        translate_config = {
            "_link": self.HIF_translate_model,
            "translate_to": translate_to
        }
        translate_config.update(self.config.dict())
        translate_retriever = Retrieve()
        translate_retriever.setup(**translate_config)

        # Setup image retriever
        image_config = {
            "_link": self.HIF_image_model,
            "_context": "{}+{}".format(query, translate_to),
            "_extend": {
                "keypath": None,
                "args": ["translation"],
                "kwargs": {},
                "extension": "images"
            }
        }
        image_retriever = Retrieve()
        image_retriever.setup(**image_config)

        # Start Celery task
        task = (
            execute_process.s(query, translate_retriever.retain()) |
            extend_process.s(image_retriever.retain(), multi=True)
        )()
        self.task = task

    def post_process(self):
        self.rsl = Retrieve().load(serialization=self.task.result).rsl

    class Meta:
        app_label = "core"
        proxy = True


class VisualTranslations(GroupProcess):

    HIF_translations = {
        "member": "language",
        "data": "translations"
    }

    def setup(self, *args, **kwargs):
        kwargs["_process"] = 'ImageTranslate'  # move to core?
        super(VisualTranslations, self).setup(*args, **kwargs)
        self.args = self.config._supported_languages
        source_language = self.config.source_language
        if source_language in self.args:
            self.args.remove(source_language)
        self.save()

    def post_process(self, *args, **kwargs):
        self.rsl = self.data  # translates keys

    class Meta:
        app_label = "core"
        proxy = True
