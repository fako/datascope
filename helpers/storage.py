from HIF.helpers.enums import ProcessStatus
from HIF.exceptions import HIFContentError



class Content(object):

    def __init__(self, *args, **kwargs):
        super(Content, self).__init__(*args, **kwargs)
        self._virtual = {}
        self._updated = False
        self._real = {} # putting this on class level is wrong and leads to recursion!

    def __getitem__(self, item):
        if not item in self._virtual:
            raise KeyError("Content does not hold instances of {}".format(item))
        return item.objects.filter(id__in=self._virtual[item])

    def dict(self):
        return self._virtual

    def __call__(self, dictionary):
        self._virtual = dictionary

    def check_retain_tuple(self, input):
        try:
            if not isinstance(input, tuple) or not isinstance(input[1],int):
                raise HIFContentError("Content class didn't receive retain tuple with correct content.")
        except IndexError:
            HIFContentError("Content class didn't receive retain tuple with correct length.")

    def add(self, tcon):
        self.check_retain_tuple(tcon)
        cls, con_id = tcon
        if cls not in self._virtual:
            self._virtual[cls] = [con_id]
        elif con_id not in self._virtual[cls]:
            self._virtual[cls].append(con_id)
        self._updated = True

    def remove(self, tcon):
        self.check_retain_tuple(tcon)
        cls, con_id = tcon
        if cls in self._virtual and con_id in self._virtual[cls]:
            self._virtual[cls].remove(con_id)
            if not self._virtual[cls]:
                del self._virtual[cls]
        self._updated = True

    def instances(self):
        if self._updated:
            for cls, con_ids in self._virtual.iteritems():
                self._real[cls] = list(cls.objects.filter(id__in=con_ids))
                for con in self._real[cls]:
                    con.load(fetch=False)
            self._updated = False

    def retain(self):
        self.instances()
        for cls, cons in self._real.iteritems():
            print "Process cons: {}".format(cons)
            for con in cons:
                con.retain()

    def release(self):
        self.instances()
        for cls, cons in self._real.iteritems():
            for con in cons:
                con.release()




class ProcessContent(Content):

    def execute(self, process):
        self.instances()
        for prc in self._real[process]:
            prc.execute()

    def subscribe(self, process, to):
        self.instances()
        for prc in self._real[process]:
            prc.subscribe(to)

    def errors(self):
        count = 0
        for cls, prc_ids in self._virtual.iteritems():
            count += cls.objects.filter(id__in=prc_ids,status__in=[ProcessStatus.ERROR, ProcessStatus.WARNING]).count()
        return count

    def waiting(self):
        count = 0
        for cls, prc_ids in self._virtual.iteritems():
            count += cls.objects.filter(id__in=prc_ids,status__in=[ProcessStatus.WAITING, ProcessStatus.SUBSCRIBED, ProcessStatus.READY]).count()
        return count




class ContentMixin(object):

    def __init__(self, *args, **kwargs):
        super(ContentMixin, self).__init__(*args, **kwargs)
        self.prcs = ProcessContent()
        self.txts = Content()