
Serializers
-----------

Once you use and store configurations there is a good change you want to transfer them to for instance a task server.
Or perhaps you'd like to initialize them from the command line.

Using the ``to_dict`` method will turn your configuration into a basic dictionary with some extra keys.
You can decorate your functions with ``load_config`` to receive these dictionaries as arguments.
The decorator will turn these dictionaries into proper configurations before passing it down to your function. ::

    from datagrowth.configuration import create_config, load_config


    config = create_config("your_app", {
        "bar": "definitely!"
    })
    dict_config = config.to_dict()

    @load_config()
    def task_function(config, arg):
        print(config.bar, arg)


    task_function("baz", config=dict_config)
    # out: definitely! baz

Alternatively you can turn your own dictionary configuration into proper configurations using ``from_dict`` ::

    from datagrowth.configuration import ConfigurationType

    config = ConfigurationType.from_dict(dict_config)

It's possible to get a hash value from a dictionary in such a way
that identical configurations will generate identical hashes.
This is useful if you need to retrieve models based on their configuration ::

    from datagrowth.configuration import get_standardized_configuration

    from your_app.models import YourModel

    config = create_config("your_app", {
        "bar": "definitely!"
    })

Last but not least it is possible to deserialize a configuration that is given to a Django command::

    from django.core.management.base import BaseCommand

    from datagrowth.configuration import DecodeConfigAction


    class Command(BaseCommand):

        def add_arguments(self, parser):
            parser.add_argument('-c', '--config',
                type=str,
                action=DecodeConfigAction,
                nargs="?",
                default={}
            )

        def handle(*args, **options):
            config = options["config"]
            print(config.foo, config.bar)

To use this on the command line you would write::

    python manage.py baz_command --config="foo=yes&bar=no"

    # out: yes no
