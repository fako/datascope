from django.db.models.loading import get_model

from celery import task

from HIF.exceptions import HIFImproperUsage


@task(name="HIF.execute_process")
def execute_process(inp, ser_prc):
    """
    Main task which executes a Process
    Input will be given as arguments for the Process
    """
    name, obj_id = ser_prc
    cls = get_model(app_label="HIF", model_name=name)
    if cls is None:
        raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
    prc = cls()
    prc.load(serialization=ser_prc)
    if type(inp) in [list, tuple]:
        prc.execute(*inp)
    else:
        prc.execute(inp)
    return prc.retain()



@task(name="HIF.flatten_process_results")
def flatten_process_results(ser_prc, key):
    """
    This task simplifies results from a Process.
    In order for other processes to use it as input
    Should not be at the end of a chain!
    """
    name, prc_id = ser_prc
    cls = get_model(app_label="HIF",model_name=name)
    if cls is None:
            raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
    prc = cls()
    prc.load(serialization=ser_prc)
    flat = []
    for results in prc.rsl:
        for rsl in results["results"]:
            flat.append(rsl[key])
    return flat


