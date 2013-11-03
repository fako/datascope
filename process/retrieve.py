from HIF.process.base import Process, Status
from HIF.exceptions import HIFHttpError40X, HIFHttpError50X, HIFHttpLinkPending, HIFEndOfInput


class Retrieve(Process):

    links = []

    _props = ["link"]

    def execute(self,*args,**kwargs):
        args = args + (self.props.link().__class__.__name__,)
        super(Retrieve, self).execute(*args,**kwargs)

    def extract_continue_url(self, link):
        return ''

    def continue_link(self, link):
        continue_url = self.extract_continue_url(link)
        if continue_url:
            continuation = self.props(props=self.kwargs)
            continuation.identifier = continue_url
            continuation.auth_link = continue_url
            continuation.setup = False
            return continuation
        else:
            raise HIFEndOfInput

    def process(self):
        link = self.props.link(props=self.kwargs)
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


