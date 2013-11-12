import sys
import pickle


def get_process_from_storage(process_tuple):

    # Load the object
    ProcessClass, process_id = process_tuple
    process = ProcessClass.objects.get(id=process_id)

    # Set configuration correctly
    process.config.namespace = ProcessClass.HIF_namespace
    process.config(pickle.loads(process.configuration))

    # Finish processing where appropriate
    if process.data and not process.results:
        process.results = process.post_process()
        process.save()

    # Return loaded object
    return process