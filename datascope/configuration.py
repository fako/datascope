from django.conf import settings

from datagrowth.configuration import DEFAULT_CONFIGURATION, MOCK_CONFIGURATION


PROCESS_CHOICE_LIST = [
    ("HttpResourceProcessor.fetch", "Fetch content from HTTP resource"),
    ("HttpResourceProcessor.fetch_mass", "Fetch content from multiple HTTP resources"),
    ("ExtractProcessor.extract_from_resource", "Extract content from one or more resources"),
    ("ExtractProcessor.pass_resource_through", "Take content 'as is' from one or more resources"),
]
