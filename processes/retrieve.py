from HIF.processes.core import Process, Status
from HIF.exceptions import HIFInputError, HIFEndOfInput, HIFEndlessLoop


class Retrieve(Process):

    def extract_continue_url(self, link):
        return ''

    def handle_exception(self, exception):
        raise exception

    def continue_link(self, link):
        continue_url = self.extract_continue_url(link)
        if continue_url:
            pass # TODO: implement properly and write tests
            #continuation = self.config.class_link(config=self.kwargs)
            #continuation.identifier = continue_url
            #continuation.auth_link = continue_url
            #continuation.setup = False
            #return continuation
        else:
            raise HIFEndOfInput

    def process(self):
        links = []
        link = self.config._link(config=self.config.dict())
        try:
            for repetition in range(100):
                links.append(link)
                #self.text_set.add(link)
                link.get(self.args[0])
                link.retain()
                link = self.continue_link(link)
            else:
                raise HIFEndlessLoop("HIF stopped retrieving links after fetching 100 links. Does extract_continuation_url ever return an empty string?")
        except HIFInputError as exception:
            self.handle_exception(exception)
        except HIFEndOfInput:
            pass
        finally:
            self.retain()

        return links

    def post_process(self):
        print "inside retrieve post_process"
        print self.data
        results = []
        for link in self.data:
            results += link.results
        return results

    class Meta:
        proxy = True