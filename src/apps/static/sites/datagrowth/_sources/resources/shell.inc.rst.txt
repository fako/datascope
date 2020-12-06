
Shell Resource
--------------

The ``ShellResource`` retrieves data from a shell command.
You'll need to create a class that inherits from ``ShellResource`` and specify a few attributes
to make a ``ShellResource`` run your commands and gather data.


Specify command
***************

Any command that a ShellResource needs to run gets passed down to the ``subprocess`` module.
That module accepts commands as a list of strings, where each element is a part of the command.
This means that a ``grep`` command that finds the string "test" in files in the current directory looks as follows::

    command = ["grep", "test", "."]

Let's assume that we want to gather data by searching for certain strings in certain directories.
Let's further assume that the strings to search for and directories to get data from can very per context.
A resource that is capable of gathering such data would look like this::

    from datagrowth.resources import ShellResource


    class MyGrepDataSource(ShellResource):

        CMD_TEMPLATE = ["grep", "{}", "{}"]


    data_source = MyGrepDataSource()
    data_source.run("test", ".")
    # data_source now contains lines of text where "test" is found in files in current directory.
    # You can call the debug method to see which command was executed exactly.
    data_source.debug()  # out: grep "test" .

    # The ShellResource is nothing but a thin Django wrapper around the subprocess module
    # You can check if the command succeeded and get the data.
    # It will return the data as unicode text by default.
    if data_source.success:
        content_type, data = data_source.content

    # Resource objects are actually Django models which can be closed to save them to the database
    data_source.close()

It's also possible to specify flags. For flags without values you don't need to do anyting extra
like ``grep's`` ``-R`` flag. Some other flags except values like ``grep's`` ``context``.
These flags need to be specified in the ``FLAGS`` attribute.
Furthermore you need to add the ``CMD_FLAGS`` element to your ``CMD_TEMPLATE``
to indicate where these flags with values should get inserted in the command.
Once this is done you can specify the values for the flags through the keyword arguments of ``run``. ::

    from datagrowth.resources import ShellResource


    class MyGrepDataSource(ShellResource):

        CMD_TEMPLATE = [
            "grep",
            "-R",
            "CMD_FLAGS",  # CMD_FLAGS gets replaced by actual flags
            "{}",
            "{}"
        ]

        FLAGS = {  # keys correspond to the kwargs of run and values to command flags
            "context": "--context="
        }

    data_source = MyGrepDataSource()
    data_source.run("test", ".", context=5)
    data_source.debug()  # out: grep -R --context=5 test .


Cleaning output
***************

It's often best to pass through as much data as you can from a ``Resource``.
That makes the ``Resource`` easier to re-use in different contexts.
However when dealing with shell commands the output can be much more than you desire and some cleanup is necessary.

There are two ways to do this:

1.  Override the ``clean_stdout`` and/or ``clean_stderr`` methods to clean data **before storage**
2.  Override the ``transform`` method to clean data **after storage**

Using the earlier example cleaning the data could look like this ::

    from datagrowth.resources import ShellResource


    class MyGrepDataSource(ShellResource):

        CMD_TEMPLATE = ["grep", "{}", "{}"]

        def clean_stdout(self, stdout):
            out = super().clean_stdout(stdout)
            return out.replace("\r", "\n")

        def clean_stdout(self, stderr):
            err = super().clean_stdout(stderr)
            return err.replace("\r", "\n"

        def transform(self, stdout):
            return stdout.replace("test", "TEST")


    data_source = MyGrepDataSource()
    data_source.run("test", ".")
    data_source.close()
    print(data_source.stdout)  # out: stdout without \r but with "test" in lowercase
    print(data_source.stderr)  # out: stderr without \r
    content_type, data = data_source.content
    print(data)  # out: stdout without \r and with "test" in uppercase


Working directory
*****************

The ``grep`` command is present globally on most systems.
However often you want to retrieve data from a command that is not system wide available.
Instead the binary of that command sits somewhere in a directory, where it got installed or compiled.
To run such commands you could prefix the command with a full path,
but that would make the ``ShellResource`` less portable.
Alternatively you can specify the ``DIRECTORY_SETTING`` attribute.
When specified the ``ShellResource`` will look for the Django setting by that name.
It then changes the working directory to the value of that setting.

For example: setting ``DIRECTORY_SETTING`` to ``"BREW_BIN_DIRECTORY"`` and adding a setting ``BREW_BIN_DIRECTORY``
with the value ``"/usr/local/bin"`` will run the command specified in the ``ShellResource`` from the Brew directory.
On a Mac that would allow retrieving data from commands like ``wget`` or ``htop`` when installed through Brew.


Environment
***********

The exact behaviour of commands is often regulated through environment variables.
You can specify these for a ``ShellResource`` by overriding the ``environment`` method.
That method receives the input from the ``run`` method and should return a dictionary with key-value pairs
that will be used as environment variables or ``None`` when no variables should get set.
If you only use static variables it's possible to define those on the ``VARIABLES`` attribute.
The default ``environment`` method returns ``VARIABLES``. ::

    from datagrowth.resources import ShellResource


    class MyShellDataSource(ShellResource):

        CMD_TEMPLATE = ["command.sh", "{}"]

        def environment(*args, **kwargs):
            mode = kwargs.pop("mode", None)
            if not mode:
                return
            return {
                "COMMAND_MODE": mode
            }

    data_source = MyShellDataSource()
    # The call below will execute whatever is in "command.sh" with a COMMAND_MODE set to "foo"
    data_source.run("test", mode="foo")
    data_source.debug()  # out: command.sh test
