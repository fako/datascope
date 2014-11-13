# HELPERS
from core.helpers.tests.configuration import *
from core.helpers.tests.data import *
from core.helpers.tests.mixins import *
from core.helpers.tests.storage import *

# INPUT
from core.input.http.tests.base import *
from core.input.http.tests.google import *
from core.input.http.tests.wiki import *

# STORAGE
from core.models.tests.storage import *

# PROCESSES




# import time
#
# from django.test import TestCase, Client
#
#
# class TestVisualTranslations(TestCase):
#
#     def test_one_word(self):
#
#         client = Client()
#         response = None
#         status = 202
#         while status == 202:
#             response = client.get('/visual-translations/', {'q': 'queen'})
#             time.sleep(1)
#             status = response.status_code
#
#         self.assertEqual(response.status_code, 200, "One word content did return 200")
#         self.assertTrue(response.content, "One word content is falsy")
#         self.assertIsInstance(response.content, list, "One word content is not a list")
#
#     def test_two_words(self):
#
#         client = Client()
#         response = None
#         status = 202
#         while status == 202:
#             response = client.get('/visual-translations/',{'q': 'queen madame'})
#             time.sleep(1)
#             status = response.status_code
#
#         self.assertEqual(response.status_code, 400, "Two words content did return 400")
#
#     def test_no_content(self):
#
#         client = Client()
#         response = None
#         status = 202
#         while status == 202:
#             response = client.get('/visual-translations/',{'q': 'singers'})
#             time.sleep(1)
#             status = response.status_code
#
#         self.assertEqual(response.status_code, 204, "Singers returned content?")
#         self.assertFalse(response.content, "Singers content is trueish")
#         self.assertIsInstance(response.content, list, "Singers content is not a list")
#
#     def test_not_found(self):
#
#         client = Client()
#         response = None
#         status = 202
#         while status == 202:
#             response = client.get('/visual-translations/',{'q': 'kjsdfhkhbsd'})
#             time.sleep(1)
#             status = response.status_code
#
#         self.assertEqual(response.status_code, 404, "kjsdfhkhbsd returned content?")
#         self.assertFalse(response.content, "kjsdfhkhbsd content is trueish")
#         self.assertIsInstance(response.content, list, "kjsdfhkhbsd content is not a list")