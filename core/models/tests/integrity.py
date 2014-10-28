from django.test import TestCase

from core.helpers.storage import get_hif_model
from core.models.storage import Storage, TextStorage, ProcessStorage


class TestModelIntegrity(TestCase):
    """
    This class tests whether a certain model follows conventions.
    Test that fail are meant as a warning for the programmer that it uses HIF differently than designed.
    """

    HIF_model = None

    def setUp(self):
        self.instance = self.HIF_model()
        self.instance.setup()

    def test_integrity_model(self):
        # See whether the model can be retrieved by get_hif_model
        model_name = self.instance.__class__.__name__
        model = get_hif_model(model_name)
        self.assertNotEquals(model, None, "{} can't be retrieved as model by Django. Does it exist, is it placed under models and does it have the HIF app_label?".format(model_name))
        # See if the model uses a correct ORM
        mro = model.mro()
        self.assertIn(Storage, mro, "{} does not inherit from Storage class.".format(model_name))
        self.assertTrue(TextStorage in mro or ProcessStorage in mro, "{} does not inherit from TextStorage or ProcessStorage.".format(model_name))
