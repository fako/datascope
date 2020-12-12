
Getting started
---------------

To get started with gathering data through resources you need to pick a ``Resource`` class
based on the data source you want to connect to.
You can choose between ``HttpResource`` (for API connections and scraping websites)
or ``ShellResource`` (for getting data from local commands).
You'll at least need to declare some class attributes on your own ``Resource`` to gather data from a source.
Before this gets explained in detail we'll demonstrate how resources are used in general.

The ``Resource`` model is the base class for all Datagrowth resources.
What follows is pseudo code to demonstrate how the flow with ``Resource`` derived classes are used to gather data.
This pseudo example uses a ``grow`` method, which currently does not exist.
Instead you would use ``get`` and ``post`` with ``HttpResource`` and ``run`` with ``ShellResource``.
These methods kick-off the data collection for their derived classes. ::

    resource = Resource(  # abstract class, instantiate derived class in real code
        config=config  # resources take a Datagrowth config to handle context
    )
    # the call below kicks-off data collection through the resource
    # "grow" is only a pseudo-method for this example
    # use "get", "post" or "run" instead of "grow" depending on the data source
    # input for the data collection can consist of args and kwargs
    resource.grow(
        "some", "input",
        session=session
    )

    if not resource.success:
        # when things go wrong it's sometimes convenient to save some context
        # "retain" stores a generic relation on resource to any other model
        resource.retain(any_django_model)
    resource.close()  # cleans and saves the resource to cache the collected data

    content_type, data = resource.content
    if data is not None:
        # handle the data ...

    # When making the exact same "grow" call again.
    # This time the data will come from the database as it has been stored before.
    resource.grow(
        "some", "input",
        session=session
    )

Retrieving the data from the database instead of the actual source is very convenient
when dealing with large data sources.
It allows for retries without starting over, it keeps resource use low and makes consequent runs much faster.
