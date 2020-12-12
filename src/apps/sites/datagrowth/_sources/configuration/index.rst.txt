.. Data Growth configuration documentation


Configurations
==============

Configurations can be serialized to JSON dicts for storage and transfer (to for instance task servers).
They can also be passed on to other configuration instances in a parent/child like relationship.
Configurations have defaults which can be set when Django loads.
These defaults are namespaced to prevent name clashes across apps.

Usually a request will set configurations during runtime to configure long running tasks.
Configurations can also be used as a bag of properties.
This is useful for Django models that have a very wide configuration range.

.. include:: usage.rst.inc

.. include:: fields.rst.inc

.. include:: updating.rst.inc

.. include:: serializers.rst.inc
