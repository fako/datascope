from rest_framework.status import HTTP_200_OK

from core.exceptions import HIFProcessingWarning


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
            exception = HIFProcessingWarning()
            message = warning.get(key, 'No details provided (key={}).'.format(key))
            detail = '{}: {}'.format(warning['type'], message)
            exception.data = {'detail': detail}
            exception.status = status
            raise exception

    return handle_results_or_404

