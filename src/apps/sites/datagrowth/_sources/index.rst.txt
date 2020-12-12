.. Data Growth documentation master file, created by
   sphinx-quickstart on Wed Dec 17 18:26:35 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Data Growth's documentation
===========================

Data Growth is the bridge between gathered data and algorithms.
The demand for data is increasing, because many algorithms and computer models need more of it than ever before.
However as the data grows it becomes increasingly complex to handle it in a Pythonic way.
Especially when it comes from many different sources.

Data Growth is a Django application that helps to gather data in an organized way. With it you can declare pipelines
for the data gathering and preprocessing as well as pipelines for filtering and redistribution.

The package offers classes that help you load the data into your models.
Or you can start the Django server to transfer data over a REST API to other devices or services.

Contents
--------

.. toctree::
   :maxdepth: 2

   resources/index
   configuration/index
   processors/index
   utils/index
   reference


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
