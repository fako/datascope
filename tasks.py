from celery import task


@task(name="HIF.execute_process")
def execute_process(input, tprc):
    """
    Main task which executes a Process
    Input will be given as arguments for the Process
    """
    cls, prc_id = tprc
    prc = cls()
    prc.load(id=prc_id)
    if type(input) in [list, tuple]:
        prc.execute(*input)
    else:
        prc.execute(input)
    return prc.retain()



@task(name="HIF.flatten_process_results")
def flatten_process_results(tprc, key):
    """
    This task simplifies results from a Process.
    In order for other processes to use it as input
    Should not be at the end of a chain!
    """
    cls, prc_id = tprc
    prc = cls()
    prc.load(id=prc_id)
    flat = []
    for results in prc.rsl:
        for rsl in results["results"]:
            flat.append(rsl[key])
    return flat


