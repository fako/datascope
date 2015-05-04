from rest_framework.status import HTTP_200_OK, HTTP_300_MULTIPLE_CHOICES

from legacy.exceptions import HIFProcessingWarning
from legacy.processes.base import Retrieve
from legacy.helpers.enums import ProcessStatus as Status


def handler_results_or_404(condition):

    def handle_results_or_404(warning, results):

        exception = HIFProcessingWarning()

        if results:
            exception.data = results
            exception.status = HTTP_200_OK
            raise exception

        cls, status, key = condition.split('|')
        status = int(status)
        if warning['type'] == cls and warning['status'] == status:
            message = warning.get(key, 'No details provided (key={}).'.format(key))
            detail = '{}: {}'.format(warning['type'], message)
            exception.data = {'detail': detail}
            exception.status = status
            raise exception

    return handle_results_or_404


def handler_wikipedia_disambiguation_300(condition):

    def handle_wikipedia_disambiguation_300(warning, results):

        exception = HIFProcessingWarning()

        cls, status, key = condition.split('|')
        status = int(status)
        if warning['type'] == cls and warning['status'] == status:

            retriever = Retrieve()
            retriever.execute(warning[key], _link="WikiLinks")

            if retriever.status != Status.DONE:
                return

            exception.data = retriever.rsl
            exception.status = HTTP_300_MULTIPLE_CHOICES
            raise exception

    return handle_wikipedia_disambiguation_300

