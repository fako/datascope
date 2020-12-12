
Input
-----

Very often when gathering data you're only interested in part of the data and can discard the rest.
The ``ExtractProcessor`` is a processor that helps you to extract data from common formats like JSON, HTML and XML.

Let's imagine a scenario where you want to get the ``name`` and ``description`` of objects in a JSON response
that are stored under the ``results`` key. Together with this you want to store the source of these objects,
which is stored under the ``source`` inside a ``metadata`` object.
It can be useful to store metadata such as a source together with the actual data for later processing.

In order to handle the scenario described above with the ``ExtractProcessor``.
You would have to write a configuration as follows ::

    from datagrowth.config import create_config
    from datagrowth.processors import ExtractProcessor


    config = create_config("extract_processor", {

        # Objectives indicate what data you want to retrieve from a source
        "objective": {

            "@": "$.results",  # '@' value specifies where to start extraction
            "#source": "$.metadata.source",  # this value is the same for all results

            # Objective items not starting with '@' or '#'
            # are looked up in the context of the '@' item
            "name": "$.name",
            "description: "$.description"
        }

    }

    extractor = ExtractProcessor(config=config)
    results = extractor.extract("application/json", """{
        "metadata": {"source": "data tooling" ... more keys you don't need }
        "results": [
            {"name": "datagrowth", description": "data mash up" ... more keys you don't need},
            {"name": "scrappy", description": "website scraping" ... more keys you don't need}
        ]
    }""")

    print(results)
    # out: [{"name": "datagrowth", description": "data mash up", "source": "data tooling"}, ...]

In this case the objective values are JSON paths.
These paths point to the data that should get extracted and ignore the rest.
Read more about how they work at the `reach function documentation <../utils/reference.html#datagrowth.utils.data.reach>`_

Instead of JSON paths you can use BeautifulSoup expressions to extract from HTML and XML.
Let's imagine a scenario where we want to get data from an unsorted HTML list.
The title of each item we want to store as ``name`` and the content as ``description``.
Lastly the ``source`` will come from the title element of the page.

For that the ``ExtractProcessor`` configuration looks like this ::

    from bs4 import BeautifulSoup

    from datagrowth.config import create_config
    from datagrowth.processors import ExtractProcessor


    config = create_config("extract_processor", {

        # Objectives indicate what data you want to retrieve from a source
        "objective": {

            # The objective items below can use the "soup" variable
            # which is the passed BeautifulSoup instance
            "@": "soup.find_all('li')",  # '@' value specifies where to start extraction
            "#source": "soup.find('title').text",  # this value is the same for all results

            # Objective items not starting with '@' or '#'
            # can use the "el" variable which in this case is a BeautifulSoup <li> tag
            # as well as the "soup" variable which is the BeautifulSoup instance
            "name": "el.attrs['title']",  # notice the transformation from 'title' to 'name'
            "description: "el.text"
        }

    }

    extractor = ExtractProcessor(config=config)
    soup = BeautifulSoup("""
        <html>
            <head><title>data tooling</title></head>
            <body>
                <ul>
                    <li title="datagrowth">data mash up</li>
                    <li title="scrappy">website scraping</li>
                <ul>
            </body>
        </html>
    """)
    results = extractor.extract("application/json", soup)

    print(results)
    # out: [{"name": "datagrowth", description": "data mash up", "source": "data tooling"}, ...]

In the case above we do a little more than extraction. We also transform a ``title`` value into a ``name`` value.
That way the output of the extractor is interchangeable with the extractor from the JSON scenario.
This can be very useful when dealing with multiple different data sources.

