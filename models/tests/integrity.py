from django.test import TestCase

from HIF.helpers.storage import get_hif_model


class TestModelIntegrity(TestCase):
    """
    The test looks at most often over ridden methods and checks input

    Perhaps we need to sublass for Query and JsonQuery
    Class should look into Domain() to see whether integration testing is wanted
    """

    HIF_model = None

    def setUp(self):
        self.instance = self.HIF_model()

    def test_integrity_model(self):
        # See whether the model can be retrieved by get_hif_model
        model = get_hif_model(self.instance.__class__.__name__)
        self.assertNotEquals(model, None, "{} can't be retrieved as model by Django. Does it exist, is it placed under models and does it have the HIF app_label?")
        # See if the model uses a correct ORM
        self.fail("continue here")
