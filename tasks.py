import json

from celery import task, group

from HIF.processes.retrieve import Retrieve


@task(name="HIF.retrieve_link")
def retrieve_link(link_class, *args, **kwargs):
    # Creates a query_link_class instance and let it find query
    retriever = Retrieve()
    retriever.execute(link_class, **kwargs)
    print retriever.results
    return json.loads(retriever.results) # problematic!


@task(name="HIF.flatten_process_results")
def flatten_process_results(process_results, key):
    # Returns all values from a specific key in process result
    return [result[key] for result in process_results]


@task(name="HIF.retrieve_multi_query_link")
def retrieve_multi_query_link(array, query_link_class, *args, **kwargs):
    # Creates a celery group with get_query_link tasks
    # Executes it in sync and returns the array of query_links
    print "Arguments: {}, {}".format(array,kwargs)
    arguments = []
    for query in array:
        argument = dict(kwargs)
        argument["query"] = query
        arguments.append(argument)
    results = {}
    grp = group(retrieve_link.s(query_link_class, **argument) for argument in arguments).apply_async()
    grp.get()
    for arg, rsl in zip(array, grp):
        results[arg] = rsl
    return results


#@task()
#def execute_process(process_id):
#    pass