
Http Resource
-------------

The ``HttpResource`` retrieves data from any HTTP source. Typically these sources are API's or websites.


Basic usage
***********

The most basic usage for fetching data from a HTTP source is inheriting from ``URLResource``,
which in turn inherits from ``HttpResource``. ::

    from collections import Count

    from datagrowth.resources import URLResource


    class MyHTTPDataSource(URLResource):
        pass


    data_source = MyHTTPDataSource()
    data_source.get("https://example.com")
    # data_source now contains the response from example.com

    # The URLResource is nothing but a thin Django wrapper around the requests library
    # You can check if the request succeeded and get the data.
    # It will return Python objects for JSON responses or BeautifulSoup instances for HTML and XML
    if data_source.success:
        content_type, data = data_source.content

    # Resource objects are actually Django models which can be closed to save them to the database
    data_source.close()
    # Using the Django ORM it is easy to query how requests did
    statuses = Counter(
        MyHTTPDataSource.objects.exclude(status=200).values_list("status", flat=True)
    )
    # And as explained above the database has other advantages like storing data already retrieved.
    # The below does not make a request, but fetches results from the database.
    # It does this because above we saved a resource to the exact same request
    data_source_cache = MyHTTPDataSource().get("https://example.com")

    # Apart from GET you can also do POST.
    # Any keyword arguments will be send as the body of the POST request.
    data_source_post = MyHTTPDataSource().post("https://example.com", example=True)


Downloading files
*****************

Usually data is available under the ``content`` property.
It is also possible to save responses to disk in files. This can be convenient to save images.
To do this you use the ``HttpImageResource``::

    from datagrowth.resources import HttpImageResource


    class MyHTTPImageSource(URLResource):
        pass

    image_source = MyHTTPImageSource()
    image_source.get("https://example.com/image.jpg")

    # The content property will now return the image file instead of data
    if image_source.success:
        content_type, image_file = image_source.content

It's also possible to save other types of files.
This can be done by using ``HttpFileResource`` instead of ``HttpImageResource``.


Customize requests
******************

In most cases it isn't sufficient to simply pass URL's to ``URLResource`` or ``HttpImageResource``.
By setting some attributes you can customize how any ``HttpResource`` fetches data::

    from datagrowth.resources import HttpResource


    class MyHTTPDataSource(HttpResource):

        URI_TEMPLATE = "https://example.com?query={}"


    data_source = MyHTTPDataSource()
    # The call below will make a request to https://example.com?query=my-query-terms
    data_source.get("my-query-terms")
    print(data_source.request)  # outputs the request being made

The ``URI_TEMPLATE`` is the most basic way to declare how resources should be fetched.
A more complete example is below. The example is using ``post``, but most attributes also work for ``get``::

    from datagrowth.resources import HttpResource


    class MyHTTPDataSource(HttpResource):

        URI_TEMPLATE = "https://example.com"

        # Add query parameters to the end of URL's with PARAMETERS
        PARAMETERS = {
            "defaults": 1
        }

        # Or add headers with HEADERS
        HEADERS = {
            "Content-Type": "application/json"
        }

        # As this resource will now be using POST we'll add default data with DATA
        DATA = {
            "default_data": 1
        }

    data_source = MyHTTPDataSource()
    # The call below makes a POST request to https://example.com?defaults=1
    # It will add a JSON content header
    # and sends a dictionary with data containing the default_data and more_data keys.
    data_source.post(more_data="Yassss")
    print(data_source.request)  # outputs the request being made

If you need more control over parameters, headers or data,
then you can override the ``parameters``, ``headers`` and ``data`` methods.
These methods by default return the ``PARAMETERS``, ``HEADERS`` and ``DATA`` attributes.
The ``data`` method will also merge in any keyword arguments coming from the call to ``post`` if applicable.


Continuation requests
*********************

Usually a response also contains some information on how to get more data from the same source.
The ``HttpResource`` provides a mechanism to easily follow up on requests made by the resource.
You'll have to override the ``next_parameters`` method to indicate which data to use for continuation requests. ::

    from datagrowth.resources import HttpResource


    class MyHTTPDataSource(HttpResource):

        URI_TEMPLATE = "https://example.com?query={}"

        def next_parameters(self):
            """
            This method looks if there is a "next" key in the response data.
            If there is none it simply returns an empty dict.
            If there is one it returns the value under a "page" key.
            """
            params = super().next_parameters()
            content_type, data = self.content
            if data is None:
                return params
            page = data.get("next", None)
            if page is None:
                return params
            params["page"] = page
            return params


    data_source = MyHTTPDataSource()
    # The call below will make a request to https://example.com?query=my-query-terms
    data_source.get("my-query-terms")
    next_request = data_source.create_next_request()
    follow_up = MyHTTPDataSource(request=next_request)
    # The call below will make a request to https://example.com?query=my-query-terms&page=1
    # Provided that the response data contains a "next" key with value 1
    follow_up.get()


Authenticating requests
***********************

Authenticating requests is very similar to other customization of a ``HttpResource``.
You need to override the ``auth_headers`` or ``auth_parameters`` methods.
The headers and/or parameters returned by these methods in a dictionary get added to the request,
but only when a request is made. This sensitive information is not getting stored in the database.
Inside the methods it's possible to use for instance the ``config`` to provide credentials.

.. warning::
    Beware that non-default values for ``config`` get stored in plain text in the database.
    So credentials shouldn't get passed to a config directly use ``register_defaults`` instead
    (see: `register defaults example </configuration/index.html#getting-started>`_)

::

    from datagrowth.resources import HttpResource


    class MyHTTPDataSource(HttpResource):

        def auth_headers(self):
            return {
                "Authorization": "Bearer {}".format(self.config.api_token)
            }
