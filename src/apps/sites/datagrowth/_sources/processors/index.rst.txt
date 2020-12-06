.. Data Growth processors documentation

Processors
==========

A processor is a plain Python class that inherits from the ``Processor`` class and that processes data in some way.
For instance to do extraction, transformation and loading of data (ETL).

Processors have two important properties:

 * They take `configurations`__ during initialisations, which can be used during processing
 * If declarations of processors occur in the ``processors`` module of a Django app it's possible to load a processor by name

These properties make it trivial to dispatch a task with the name of the processor (as a string) and some configuration (as JSON)
to for instance Celery and do parallel processing and/or processing in a pipeline fashion.

You can create your own processors or use pre-made processors from a Django app.
To start using Datagrowth processors include datagrowth as an app in your ``INSTALLED_APPS`` setting ::

    INSTALLED_APPS = (
        ...
        'datagrowth',
    )


The first type of processors that Datagrowth ships with is processors that handle input.

.. include:: input.inc.rst

.. include:: custom.inc.rst


.. _configuration_getting_started: ../configuration

__ configuration_getting_started_
