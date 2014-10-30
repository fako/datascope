from core.processes.base import Process, Retrieve, GroupProcess
from core.tasks import execute_process, extend_process


class VisualTranslation(Process):

    # HIF interface
    HIF_translate_model = "WikiTranslate"  # core.input.http.wiki
    HIF_image_model = "GoogleImage"  # core.input.http.google
    HIF_video_model = "YouTubeSearch"  # core.input.http.google
    HIF_namespace = 'translate'

    def get_translate_retriever(self):
        """

        :return:
        """
        translate_config = {
            "_link": self.HIF_translate_model,
            "translate_to": self.config.translate_to
        }
        translate_config.update(self.config.dict())
        translate_retriever = Retrieve()
        translate_retriever.setup(**translate_config)
        return translate_retriever

    def get_visual_retriever(self, medium):
        """

        :param medium:
        :return:
        """
        model = self.HIF_image_model if medium == 'images' else self.HIF_video_model
        image_config = {
            "_link": model,
            "_context": "{}+{}+{}".format(self.config.query, self.config.translate_to, medium),
            "_extend": {
                "keypath": None,
                "args": ["translation"],
                "kwargs": {},
                "extension": medium
            }
        }
        visual_retriever = Retrieve()
        visual_retriever.setup(**image_config)
        return visual_retriever

    def process(self):
        translate_retriever = self.get_translate_retriever()
        task = execute_process.s(self.config.query, translate_retriever.retain())

        for medium in self.config.media.split(','):
            retriever = self.get_visual_retriever(medium)
            task |= extend_process.s(retriever.retain(), multi=True)

        self.task = task()

    def post_process(self):
        self.rsl = Retrieve().load(serialization=self.task.result).rsl

    class Meta:
        app_label = "core"
        proxy = True


class VisualTranslations(GroupProcess):

    HIF_group_process = 'VisualTranslation'
    HIF_group_vary = 'translate_to'

    def process(self):
        if not self.args:
            self.args = self.config._supported_languages
            source_language = self.config.source_language
            if source_language in self.args:
                self.args.remove(source_language)
        super(VisualTranslations, self).process()

    class Meta:
        app_label = "core"
        proxy = True
