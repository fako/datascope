
Getting started
---------------

In your apps using the ready method of the AppConfig you can register default configurations
using the ``register_defaults`` function
::
    from django.apps import AppConfig

    from datagrowth.configuration import register_defaults


    class YourAppConfig(AppConfig):
        name = 'your_app'

        def ready(self):
            register_defaults("your_app", {
                "your_configuration": True,
                "very_special": False
            })


Once defaults are specified you can create and use configurations with ``create_config``
::

    from datagrowth.configuration import create_config

    config = create_config("your_app", {
        "very_special": "definitely!"
    })

    print(config.your_configuration)
    # out: True
    print(config.very_special)
    # out: "definitely!"

