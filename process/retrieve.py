from HIF.process.base import Process, Status
from HIF.exceptions import HIFHttpError40X, HIFHttpError50X, HIFHttpLinkPending, HIFEndOfInput


class Retrieve(Process):
    link_class = None
    links = []

    def extract_continue_url(self, link):
        return ''

    def continue_link(self, link):
        continue_url = self.extract_continue_url(link)
        if continue_url:
            continuation = self.link_class(*self.args, **self.kwargs)
            continuation.identifier = continue_url
            continuation.auth_link = continue_url
            continuation.setup = False
            return continuation
        else:
            raise HIFEndOfInput

    def __init__(self, *args, **kwargs):
        try:
            self.link_class = kwargs["target"]
            del(kwargs["target"])
        except KeyError:
            pass
        super(Retrieve, self).__init__(*args,**kwargs)


    def process(self):
        link = self.link_class(*self.args, **self.kwargs)
        try:
            while True:
                self.links.append(link)
                link.get()
                link = self.continue_link(link)
        except HIFHttpError50X:
            self.status = Status.EXTERNAL_SERVER_ERROR
        except HIFHttpError40X:
            self.status = Status.EXTERNAL_REQUEST_ERROR
        except HIFHttpLinkPending:
            self.status = Status.WAITING
        except HIFEndOfInput:
            self.status = Status.DONE

        if self.status != Status.DONE:
            for link in self.links:
                link.hibernate()

        return self.status

    def post_process(self):
        results = []
        for link in self.links:
            results += link.results
        return results

    class Meta:
        proxy = True


