import json

from django.db.models import fields
from django.forms import fields as form_fields
from django.core.exceptions import ValidationError

from .types import ConfigurationProperty


class ConfigurationFormField(form_fields.CharField):
    """
    This form field correctly serializes the configuration inside of text area's when saving an (admin) form.
    """
    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Enter valid JSON")
        return super(ConfigurationFormField, self).to_python(value)


class ConfigurationField(fields.TextField):
    """
    This field creates a property of ConfigurationType on Django models.
    All values will be saved in the database upon save of a model.

    All initialization parameters are optional and act as defaults.
    By setting ``CONFIG_NAMESPACE``, ``CONFIG_PRIVATE`` or ``CONFIG_DEFAULTS`` on inheriting classes
    these defaults get overridden.

    The use of ``config_defaults`` or ``CONFIG_DEFAULTS`` is discouraged.
    Because setting this value makes it impossible to change the defaults at runtime.
    If you want to set defaults for a field it's recommended to use the DATAGROWTH_DEFAULT_CONFIGURATION setting or
    ``register_defaults`` if you want to set defaults at runtime.

    :param namespace: (string) prefix to search default configurations with if a configuration is missing
    :param private: (list) keys that are considered as private
    :param config_defaults: (dict) should hold default configurations as items
    :param args: additional TextField arguments
    :param kwargs: additional TextField keyword arguments
    """

    form_class = ConfigurationFormField

    def __init__(self, namespace="global", private=("_private", "_namespace", "_defaults",),
                 config_defaults=None, *args, **kwargs):
        """
        Stores its arguments for later use by contribute_to_class.
        The arguments are passed directly to the ConfigurationType class by the  contribute_to_class method.
        Except when ``CONFIG_DEFAULTS``, ``CONFIG_NAMESPACE`` or ``CONFIG_PRIVATE`` are set on the owner class.
        In that case these values get passed on to the ConfigurationType.
        """
        super(ConfigurationField, self).__init__(*args, **kwargs)
        self._namespace = namespace
        self._private = private
        self._defaults = config_defaults

    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        configuration_property = ConfigurationProperty(
            storage_attribute=name,
            defaults=getattr(cls, 'CONFIG_DEFAULTS', self._defaults),
            namespace=getattr(cls, 'CONFIG_NAMESPACE', self._namespace),
            private=getattr(cls, 'CONFIG_PRIVATE', self._private)
        )
        setattr(cls, name, configuration_property)
        super(ConfigurationField, self).contribute_to_class(cls, name)

    def from_db_value(self, value, expression, connection, context):
        return json.loads(value)

    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Enter valid JSON: " + value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return "{}"
        if not isinstance(value, dict):
            value = value.to_dict(private=True, protected=True)
        return json.dumps(value)

    def value_from_object(self, obj):
        value = super(ConfigurationField, self).value_from_object(obj)
        if self.null and value is None:
            return None
        return json.dumps(value.to_dict(private=True, protected=True))

    def formfield(self, **kwargs):
        if "form_class" not in kwargs:
            kwargs["form_class"] = self.form_class
        field = super(ConfigurationField, self).formfield(**kwargs)
        if not field.help_text:
            field.help_text = "Enter valid JSON"
        return field
