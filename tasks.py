from django.db.models.loading import get_model

from celery import task

from HIF.exceptions import HIFImproperUsage, HIFNoContent
from HIF.helpers.storage import get_hif_model
from HIF.helpers.data import reach


@task(name="HIF.execute_process")
def execute_process(inp, ser_prc):
    """
    Main task which executes a Process
    Input will be given as arguments for the Process
    """
    Process = get_hif_model(ser_prc)
    process = Process().load(serialization=ser_prc)

    if type(inp) in [list, tuple]:
        process.execute(*inp)
    else:
        process.execute(inp)

    return process.retain()


@task(name="HIF.extend_process")
def extend_process(ser_extendee, ser_extender):
    """
    Will extend data of the extendee by using the extender.
    """
    Extender = get_hif_model(ser_extender)
    extender = Extender().load(serialization=ser_extender)

    extender.setup()
    extender.extend(ser_extendee)  # TODO: try block with a return

    extender.execute()
    extender.retain()

    return ser_extendee


# TODO: rewrite what is using this to use extend_process instead
# TODO: remove this code as it is outdated and inferior
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
    try:
        for rsl in prc.rsl:
            flat.append(rsl[key])
    except HIFNoContent:
        pass
    return flat
