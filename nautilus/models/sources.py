from core.models.resources.http import HttpResource


class LocaforaLogin(HttpResource):

    URI_TEMPLATE = "http://locafora.nl/api/person/model_login"

    PARAMETERS = {
        "format": "json"
    }


class LocaforaOrders(HttpResource):

    URI_TEMPLATE = "http://locafora.nl/api/order/collection?status[]=1&status[]=2"

    PARAMETERS = {
        "format": "json",
        "limit": 25,
        "offset": 0,
        "is_deleted": 0,
        "shop_id": 18872,
        "supplier_person_id": 17623
    }

    class Meta:
        verbose_name = "Locafora order"
        verbose_name_plural = "Locafora orders"