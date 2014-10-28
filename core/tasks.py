from django.db.models.loading import get_model

from celery import task

from HIF.exceptions import HIFImproperUsage, HIFNoContent
from HIF.helpers.storage import get_hif_model, copy_hif_model
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
def extend_process(ser_extendee, ser_extender, multi=False, register=True, finish=True):
    """
    Will extend data of the extendee by using the extender.
    """
    Extender = get_hif_model(ser_extender)
    extender = Extender().load(serialization=ser_extender)
    extender.setup()
    Extendee = get_hif_model(ser_extendee)
    extendee = Extendee().load(serialization=ser_extendee)
    extendee.setup()
    # TODO: should set status to 2, correct, or maybe a special extending status?

    extenders = []
    if not multi:
        extenders.append(extender)
    else:
        base_keypath = extender.config._extend['keypath']
        input_list = reach(base_keypath, extendee.rsl)
        for ind, inp in enumerate(input_list):
            # TODO: below can be done nicer probably
            extndr = copy_hif_model(extender)
            keypath = "{}.{}".format(base_keypath, ind) if base_keypath is not None else unicode(ind)
            extndr.config._extend["keypath"] = keypath
            extndr.setup()
            extndr.identification = extndr.identifier()
            extndr.retain()
            extenders.append(extndr)
        # Make sure we can garbage collect the base extend class correctly
        extendee.rgs.add(ser_extender)
        extendee.retain()


    for extndr in extenders:
        if register:
            ser_extndr = extndr.retain()
            extendee.rgs.add(ser_extndr)
            extendee.ext.add(ser_extndr)  # Maybe make Containers push to X number of fields?
            extendee.retain()

        extndr.extend(ser_extendee)  # TODO: try block with a return
        extndr.execute()

    if finish:
        extendee.merge_extensions()
        extendee.retain()

    return ser_extendee


@task(name="HIF.finish_extend")
def finish_extend(extendee_list):
    extendee = extendee_list[0]
    extendee.merge_extensions()
    return extendee.retain()


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

