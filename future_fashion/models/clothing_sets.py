from django.db import models
from rest_framework import serializers


class ColorClothingSet(models.Model):

    email = models.EmailField(null=True, blank=True)
    processing_permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    top_color = models.CharField(max_length=6)
    bottom_color = models.CharField(max_length=6)
    match_style = models.CharField(max_length=20, null=True, blank=True)

    top_item = models.ForeignKey("core.Individual", related_name="+", on_delete=models.DO_NOTHING)
    bottom_item = models.ForeignKey("core.Individual", related_name="+", on_delete=models.DO_NOTHING)

    def top_item_image(self):
        return u'<img width="100px" src="{}" /><div>{}</div'.format(
            self.top_item["path"].replace("future_fashion/data", ""),
            self.top_item["name"]
        )
    top_item_image.short_description = 'Top item'
    top_item_image.allow_tags = True

    def bottom_item_image(self):
        return u'<img width="100px" src="{}" /><div>{}</div>'.format(
            self.bottom_item["path"].replace("future_fashion/data", ""),
            self.bottom_item["name"]
        )
    bottom_item_image.short_description = 'Bottom item'
    bottom_item_image.allow_tags = True

    def top_item_name(self):
        return


class ColorClothingSetSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data.get("email", None) and not data.get("processing_permission", None):
            data["email"] = None
        return data

    class Meta:
        model = ColorClothingSet
        fields = "__all__"
