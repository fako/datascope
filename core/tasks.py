from django.db.models.loading import get_model

from celery import task

from core.exceptions import HIFImproperUsage, HIFNoContent
from core.helpers.storage import get_hif_model, copy_hif_model
from core.helpers.data import reach


@task(name="core.execute_process")
def execute_process(inp, ser_prc):
    """
    Main task which executes a Process
    Input will be given as arguments for the Process
    """
    Process = get_hif_model(ser_prc)
    process = Process().load(serialization=ser_prc)

    if type(inp) in [list, tuple]:
        process.execute(*inp)
    elif inp:
        process.execute(inp)
    else:
        process.execute()

    return process.retain()


@task(name="core.extend_process")
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
            extndr.identity = extndr.identify()
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


@task(name="core.finish_extend")
def finish_extend(extendee_list):
    extendee = extendee_list[0]
    extendee.merge_extensions()
    return extendee.retain()
