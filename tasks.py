from celery import task

from HIF.helpers.storage import get_process_from_storage


@task(name="HIF.flatten_process_results")
def flatten_process_results(process_id, key):
    process = get_process_from_storage(process_id)
    rsl = [result[key] for result in process]
    return rsl


@task(name="HIF.execute_process")
def execute_process(input, process_id):
    print "executing"
    process = get_process_from_storage(process_id)
    if type(input) in [list, tuple]:
        process.execute(*input)
    else:
        process.execute(input)
    print "executed"
    return process.retain()
