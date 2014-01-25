from django.test import TestCase
from django.db.models.query import QuerySet

from HIF.exceptions import HIFImproperUsage
from HIF.helpers.storage import get_hif_model, deserialize, Container
from HIF.models.storage import TextStorage


class TestHelperStorageFunctions(TestCase):

    def test_get_hif_model(self):
        model = get_hif_model("TextStorage")
        self.assertIs(model, TextStorage)
        try:
           get_hif_model("DoesNotExist")
           self.fail("get_hif_model returned DoesNotExist as a HIF model")
        except HIFImproperUsage as exception:
           self.assertEqual(str(exception), "The specified model does not exist, is not imported in models " +
                                            "or is not registered as Django model with HIF label.")

    def test_deserialize(self):
        model, id = deserialize(("TextStorage", 0,))
        self.assertEqual(model, "TextStorage")
        self.assertEqual(id, 0)
        try:
            deserialize((1, 1,))
            self.fail("deserialize excepts an int as first element in tuple")
        except HIFImproperUsage as exception:
            self.assertEqual(str(exception), "Model in serialization tuple is not stringish but <type 'int'>.")
        try:
            deserialize(("TextStorage", "0",))
            self.fail("deserialize excepts a string as second element in tuple")
        except HIFImproperUsage as exception:
            self.assertEqual(str(exception), "Object id in serialization is not an numberish, but <type 'str'>.")
        try:
            deserialize(("TextStorage",))
            self.fail("deserialize excepts a tuple that is too short")
        except HIFImproperUsage as exception:
            self.assertEqual(str(exception), "Serialization tuple is too short.")
        try:
            deserialize(["TextStorage", 0])
            self.fail("deserialize excepts an array as argument")
        except HIFImproperUsage as exception:
            self.assertEqual(str(exception), "Serialization is not a tuple.")


class TestContainer(TestCase):

    fixtures = ['test-storage']

    @classmethod
    def setUpClass(cls):
        cls.valid = {
            "TextStorage": [1,3]
        }
        cls.invalid_keys = {
            "DoesNotExist": [1,2,3]
        }
        cls.invalid_values = {
            "TextStorage": "error"
        }
    #
    # def setUp(self):
    #     self.mixin = MockDataMixin()

    def test_init(self):
        instance = Container({})
        self.assertEqual(instance._container, {})
        instance = Container(self.valid)  # invalid input tested by test_call
        self.assertEqual(instance._container, self.valid)

    def test_call(self):
        instance = Container()
        # Valid input
        instance(self.valid)
        self.assertEqual(instance._container, self.valid)
        # Invalid keys
        try:
            instance(self.invalid_keys)
            self.fail("Invalid key didn't raise an exception")
        except HIFImproperUsage as exception:
            self.assertEqual(
                str(exception),
                "Dict given to Container contains a key DoesNotExist, which raises an exception in get_hif_model"
            )
        # Invalid values
        try:
            instance(self.invalid_values)
            self.fail("Invalid values didn't raise an exception")
        except HIFImproperUsage as exception:
            self.assertEqual(
                str(exception),
                "Dict given to Container contains invalid value for key TextStorage"
            )

    def test_dict(self):
        instance = Container(self.valid)
        self.assertEqual(instance.dict(), instance._container)

    def test_get_item(self):
        instance = Container(self.valid)
        try:
            instance["DoesNotExist"]
            self.fail("Container doesn't raise KeyError on invalid keys")
        except KeyError as exception:
            self.assertEqual(str(exception), "'Container does not hold instances of DoesNotExist'")
        query_set = instance["TextStorage"]
        self.assertIsInstance(query_set, QuerySet)
        self.assertIsInstance(query_set[0], TextStorage)
        self.assertEqual(query_set.count(), 2)

    def test_add(self):
        instance = Container()
        try:
            instance.add(("DoesNotExist", 1,))
            self.fail("Add didn't warn about a non-existing model")
        except Exception:
            pass
        instance.add(("TextStorage", 1,))
        instance.add(("TextStorage", 3,))
        self.assertEqual(instance._container, self.valid)

    def test_remove(self):
        instance = Container(init=self.valid)
        instance.remove(("DoesNotExist", 1))
        self.assertEqual(instance._container, self.valid)
        instance.remove(("TextStorage", 3))
        self.assertEqual(instance._container, {"TextStorage": [1]})
        instance.remove(("TextStorage", 1))
        self.assertEqual(instance._container, {})

    def test_run(self):
        self.fail("continue here")

    def test_query(self):
        self.fail("continue here")

    def test_count(self):
        self.fail("continue here")
