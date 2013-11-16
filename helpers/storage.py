from django.db import models

from HIF.helpers.enums import ProcessStatus




class Content(object):

    _virtual = {}
    _updated = False
    _real = {}

    def __getitem__(self, item):
        if not item in self._virtual:
            raise KeyError("Content does not hold instances of {}".format(item))
        return item.objects.filter(id__in=self._virtual[item])

    def dict(self):
        return self._virtual

    def __call__(self, dictionary):
        self._virtual = dictionary

    def add(self, tcon):
        cls, con_id = tcon
        if cls not in self._virtual:
            self._virtual[cls] = [con_id]
        elif con_id not in self._virtual[cls]:
            self._virtual[cls].append(con_id)
        self._updated = True

    def remove(self, tcon):
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
        pass
        #self.instances()
        #for cls, cons in self._real.iteritems():
        #    print "Process cons: {}".format(cons)
        #    for con in cons:
        #        con.retain()

    def release(self):
        pass
        #self.instances()
        #for cls, cons in self._real.iteritems():
        #    for con in cons:
        #        con.release()




class ProcessContent(Content):

    def execute(self, prc):
        self.instances()
        for prc in self._real[prc]:
            prc.execute()

    def subscribe(self, prc, to):
        self.instances()
        for prc in self._real[prc]:
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

