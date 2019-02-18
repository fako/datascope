
Updating
--------

You may need to update a configuration stored on a model based on information that comes from a different source.
For example with information from a request. This is possible using the ``updates`` method::

    def foo_view(request, pk):
        instance = FooModel.objects.get(id=pk)
        request_configuration = request.GET.dict()
        # Sanitize the user input to make sure no dangerous/unwanted configurations can take place
        instance.update(request_configuration)
        # Do something with the instance. It's configuration will be adjusted to the request.

Alternatively you can use the ``supplement`` method in the above example.
This method acts exactly like ``update``, but it skips any configurations that are already in existance.
You can use ``supplement`` if you want to be sure that configurations set by the system are not overwritten by a user.
