from django.test import TestCase


class CommunityTestMixin(TestCase):
    pass


class TestCommunityMock(CommunityTestMixin):
    fixtures = ["test-community"]
