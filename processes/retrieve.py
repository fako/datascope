from HIF.processes.core import Process, Status
from HIF.exceptions import HIFHttpError40X, HIFHttpError50X, HIFHttpLinkPending, HIFEndOfInput, HIFEndlessLoop


class Retrieve(Process):

    links = []
    class_link = None

    def execute(self,*args,**kwargs):
        self.class_link = args[0]
        return super(Retrieve, self).execute(*args,**kwargs)

    def extract_continue_url(self, link):
        return ''

    def continue_link(self, link):
        continue_url = self.extract_continue_url(link)
        if continue_url:
            continuation = self.class_link(config=self.kwargs)
            continuation.identifier = continue_url
            continuation.auth_link = continue_url
            continuation.setup = False
            return continuation
        else:
            raise HIFEndOfInput

    def process(self):
        self.links = []
        link = self.class_link(config=self.kwargs)
        try:
            for repetition in range(100):
                self.links.append(link)
                link.get()
                link = self.continue_link(link)
            else:
                raise HIFEndlessLoop("HIF stopped retrieving links after fetching 100 links. Does extract_continuation_url ever return an empty string?")
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
                link.retain()

        return self.status

    def post_process(self):
        results = []
        for link in self.links:
            print self.links
            results += link.results
        return results

    def retain(self):
        for link in self.links:
            if not link in self.text_set.all():
                self.text_set.add(link)
            link.retain()
        super(Retrieve, self).retain()

    def release(self):
        for link in self.text_set.all():
            self.text_set.remove(link)
        super(Retrieve, self).release()

    class Meta:
        proxy = True


