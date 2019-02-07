
Getting started
---------------

In your apps using the ready method of the AppConfig you can register default configurations
using the ``register_defaults`` function
::
    from django.apps import AppConfig

    from datagrowth.configuration import register_defaults


    class FooAppConfig(AppConfig):
        name = 'your_app'

        def ready(self):
            register_defaults("foo_app", {
                "foo": True,
                "bar": False
            })


Once defaults are specified you can create and use configurations with ``create_config`` anywhere in your code.
::
    from datagrowth.configuration import create_config

    config = create_config("your_app", {
        "bar": "definitely!"
    })

    print(config.foo)
    # out: True
    print(config.bar)
    # out: "definitely!"
    print(config.baz)
    # raises ConfigurationNotFoundError

This is the simplest way to use Datagrowth configurations.
Things get a little bit more interesting when you use Django field configurations.
