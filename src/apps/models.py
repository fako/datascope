import os

from django.conf import settings
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.translation import override, gettext_lazy as _, gettext
from django.core.exceptions import ValidationError
from django.templatetags.static import static

from core.models import TimestampMixin, SiteMixin
from apps.templatetags.app_static import app_static


class WebappTypes:
    WEBPACK = gettext("Webpack")
    PAGE = gettext("Page")

WEBAPP_TYPE_CHOICES = [
    (value, _(value)) for attr, value in sorted(WebappTypes.__dict__.items()) if not attr.startswith("_")
]


class Webapp(TimestampMixin, SiteMixin):

    route = models.CharField(_("route"), max_length=256, db_index=True)
    language = models.CharField(_("locale"), max_length=5, choices=settings.LANGUAGES, db_index=True)
    type = models.CharField(_("type"), max_length=20, choices=WEBAPP_TYPE_CHOICES)

    package = models.CharField(_("package"), max_length=50)
    version = models.CharField(_("version"), max_length=8, null=True, blank=True)

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), max_length=255)
    static_image = models.CharField(_("static image"), max_length=255, null=True, blank=True)
    tracker = models.CharField(_("tracker"), max_length=255, null=True, blank=True)

    def build_absolute_uri(self):
        with override(self.language):
            path = reverse(self.route)
        return "//{}{}".format(self.site.domain, path)

    @property
    def statics_prefix(self):
        if self.type == WebappTypes.PAGE:
            return "apps/{}/".format(self.package)
        elif self.type == WebappTypes.WEBPACK:
            return "builds/{}/{}/".format(self.package, self.version)

    def static_image_absolute_uri(self):
        if not self.static_image:
            return ""
        static_path = app_static(self, self.static_image)
        return "//{}{}".format(self.site.domain, static_path)

    def get_app_static(self, file_path):
        return static(os.path.join(self.statics_prefix, file_path))

    @property
    def locale(self):
        """
        This locale format satisfies Facebook.
        We should consider migrating everything to this format.
        """
        countries_by_language = {
            "en": "US",
            "nl": "NL"
        }
        return "{}_{}".format(self.language, countries_by_language[self.language])

    def clean(self):
        try:
            reverse(self.route)
        except NoReverseMatch:
            raise ValidationError(
                _('No reverse match found for route "%(route)s". Please specify a valid route.') % {"route": self.route}
            )
        if self.type == WebappTypes.WEBPACK and not self.version:
            raise ValidationError(_("Webapps of type webpack should specify a package version."))

    def __str__(self):
        return "{} ({})".format(self.route, self.language)

    class Meta:
        unique_together = ("route", "language",)
