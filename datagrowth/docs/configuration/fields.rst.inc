
Django fields
-------------

When you need a flexible way of configuration, without creating model fields for every option.
Then you can consider the Datagrowth ConfigurationField.
It can act as a bag-of-properties on your model.
Or a family of models if you use it on an abstract model.
Here is a basic usage example:
::
    from django.db import models

    from datagrowth.configuration import ConfigurationField


    class FooModel(models.Model):
        config = ConfigurationField(namespace="foo")

        def foo(self):
            print(self.config.bar)

Then somewhere in your code you can initialise this model with a configuration dictionary
::
    instance = FooModel(config={"bar": True})
    instance.foo()
    # out: True


You can set defaults for ConfigurationField through the ``DATAGROWTH_DEFAULT_CONFIGURATION`` setting.
Any keys in that dictionary need to get prefixed with ``foo_``.
Or you can pass a dictionary without prefixes to the ``register_defaults`` function
with ``foo`` as the namespace argument.

When models inherit from each other it is possible to change the namespace for the child class
by using ``CONFIG_NAMESPACE``.
::
    class BarModel(FooModel)

        CONFIG_NAMESPACE = "baz"

    instance = BarModel(config={})
    instance.foo()  # will look for a configuration named baz_bar in the defaults


The above model will look for default configurations prefixed with ``baz_``.
If the configuration is not there and there is no default a ``ConfigurationNotFoundError`` exception gets raised.
