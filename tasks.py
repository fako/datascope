from celery import task, group

@task(name="HIF.get_query_link")
def get_query_link(query, query_link_class, *args, **kwargs):
    # Creates a query_link_class instance and let it find query
    query_link = query_link_class(*args, **kwargs)
    query_link.get(query)
    # Returns query_link instance
    return query_link

@task(name="HIF.flatten_query_link")
def flatten_query_link(query_link_result, key):
    # Added as a chain to a query_link
    # Returns all values from a specific key
    return [query_link[key] for query_link in query_link_result]

@task(name="HIF.get_multi_query_link")
def get_multi_query_link(list_result, query_link_class):
    # Creates a celery group with get_query_link tasks
    # Executes it in sync and returns the array of query_links
    result = group(get_query_link.s(query, query_link_class) for query in list_result).apply_async()
    result.get()
    return result.join()


#@task()
#def execute_process(process_id):
#    pass