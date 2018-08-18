import json

from django.db.models import fields
from django.forms import fields as form_fields
from django.core.exceptions import ValidationError

from .types import ConfigurationProperty


class ConfigurationFormField(form_fields.CharField):
    """
    This form field correctly serializes the configuration when saving an (admin) form.
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
    This field creates a property of ConfigurationType on models.

    NB: default that gets stored in the database is always an empty dictionary.
    """
    form_class = ConfigurationFormField

    def __init__(self, config_defaults=None, namespace="", private=tuple(), *args, **kwargs):
        """
        Stores its arguments for later use by contribute_to_class.
        Assertions are done by the ConfigurationType class, upon contribute_to_class.

        :param config_defaults: (dict) that should hold default configurations as items
        :param namespace: (string) prefix to search default configurations with
        :param private: (list) keys that are considered as private
        :param args: additional field arguments
        :param kwargs: additional field keyword arguments
        :return:
        """
        super(ConfigurationField, self).__init__(*args, **kwargs)
        self._defaults = config_defaults
        self._namespace = namespace
        self._private = private

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
                # due to legacy some fixtures may contain stringyfied dicts instead of JSON objects
                # uncomment below and comment the raise statement to fix this during fixture load
                # value = dict(eval(value))
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
