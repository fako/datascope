.. Data Growth resources documentation

Resources
=========

A Resource is a Django abstract model designed to easily connect to a data source.
Currently such data sources can be:

* API's
* Shell commands
* Websites

The Resource makes connecting to data sources easier because:

* It leverages common patterns in retrieving data, which means you can write less code
* Once retrieved it will store data and return that data on subsequent uses
* Any Django model can "retain" the Resource meaning the data gets stored indefinitely
* Resources use the Datagrowth configurations which makes them re-usable in different contexts

.. include:: usage.inc.rst

.. include:: http.inc.rst

.. include:: shell.inc.rst
