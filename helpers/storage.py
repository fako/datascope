import pickle

from HIF.helpers.enums import ProcessStatus

def get_process_from_storage(process_tuple):

    # Load the object
    ProcessClass, process_id = process_tuple
    process = ProcessClass.objects.get(id=process_id)

    # Set configuration correctly
    process.config(pickle.loads(process.configuration))

    # Finish processing where appropriate
    if process.data and not process.status == ProcessStatus.DONE:
        process.post_process()
        if process.results is not None:
            process.status = ProcessStatus.DONE
            process.retain()

    # Return loaded object
    return process