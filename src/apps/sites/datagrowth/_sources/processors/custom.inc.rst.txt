
Custom made
-----------

It can be useful to create a ``Processor`` that others can use
or it can be cleaner to use a ``Processor`` with Datagrowth where you could use other means.

We'll illustrate how to create your own ``Processor`` and use it with an ``ExtractionProcessor``.
You'll see that when extracting HTML or XML it's a much cleaner method than using BeautifulSoup strings.

First we'll show you how an extraction configuration could look when using a custom processor ::

    config = create_config("extraction_processor", {

        # Objectives indicate what data you want to retrieve from a source
        "objective": {

            # The DataToolingExtractor is a class we'll define later
            # It will have methods like get_entries and get_source
            "@": "DataToolingExtractor.get_entries",
            "#source": "DataToolingExtractor.get_source",
            "name": "DataToolingExtractor.get_name",
            "description: "DataToolingExtractor.get_description"
        }

    }

The big advantage of using a processor over embedding functions in your objective directly
is that you'll be able to serialize the objective to for instance JSON and transfer it over the wire.

To create the ``DataToolingExtractor`` that we can use with the ``ExtractionProcessor``.
You'll need to create a ``processors`` module and place it inside of an installed Django app.

Inside that module you can create processors by inheriting from the ``Processor`` class ::

    from datagrowth.processors import Processor


    class DataToolingExtractor(Processor):

        @classmethod
        def get_entries(cls, soup):
            return soup.find_all('li')

        @classmethod
        def get_source(cls, soup):
            title = soup.find('title')
            return title.text if title else None

        @classmethod
        def get_name(cls, soup, el):
            return el.attrs.get("title", None)

        @classmethod
        def get_description(cls, soup, el):
            return el.text

You can also use processors from your own code.
There are class methods on ``Processor`` called ``create_processor`` and ``get_processor_class``
that can help you do that.
Read more about them in the `Processor reference <reference.html#module-datagrowth.processors.base>`_

