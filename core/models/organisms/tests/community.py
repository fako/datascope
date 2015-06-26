from django.test import TestCase

from mock import Mock, patch

from core.models.organisms import Individual, Collective, Growth
from core.models.organisms.tests.mixins import TestProcessorMixin
from core.tests.mocks.community import CommunityMock
from core.exceptions import DSProcessUnfinished



class CommunityTestMixin(TestProcessorMixin):

    def test_set_kernel(self):
        # Test that return type is an organism
        # No save!
        pass

    def test_initial_input(self):
        # Test that return type is an organism
        pass


class TestCommunityMock(CommunityTestMixin):

    fixtures = ["test-community"]

    def setUp(self):
        super(TestCommunityMock, self).setUp()
        self.instance = CommunityMock.objects.get(id=1)
        self.incomplete = CommunityMock.objects.get(id=2)

    def raise_unfinished(self, result):
        raise DSProcessUnfinished("Raised for test")

    def set_instance_mocks(self):
        self.instance.call_begin_callback = Mock()
        self.instance.call_finish_callback = Mock()

    def test_get_or_create_by_input(self):
        self.skipTest("not tested")

    def test_callbacks(self):
        self.instance.begin_phase1 = Mock()
        self.instance.finish_phase1 = Mock()
        self.instance.call_begin_callback("phase1", "input")
        self.assertTrue(self.instance.begin_phase1.called)
        self.instance.call_finish_callback("phase1", "output", "errors")
        self.assertTrue(self.instance.finish_phase1.called)

    def test_create_organism(self):
        result = self.instance.create_organism("Individual", {"test": "test"})
        self.assertGreater(result.id, 0)
        self.assertIsInstance(result, Individual)
        self.assertEqual(result.community, self.instance)
        self.assertEqual(result.schema, {"test": "test"})
        result = self.instance.create_organism("Collective", {"test": "test"})
        self.assertGreater(result.id, 0)
        self.assertIsInstance(result, Collective)
        self.assertEqual(result.community, self.instance)

    def test_setup_growth(self):
        self.instance.setup_growth()
        self.assertEqual(self.instance.growth_set.count(), 2)
        growth1 = self.instance.growth_set.first()
        growth2 = self.instance.growth_set.last()
        self.assertEqual(growth1.output.id, growth2.input.id)
        self.assertEqual(growth1.contribute, "ExtractProcessor.extract_resource")
        self.assertEqual(growth1.contribute_type, "Append")
        self.assertIsInstance(growth1.input, Individual)
        self.assertIsInstance(growth1.output, Collective)

    def test_next_growth(self):
        result = self.incomplete.next_growth()
        self.assertEqual(result.id, 2)
        result.state = "Complete"
        result.save()
        try:
            self.incomplete.next_growth()
            self.fail("Community.next_growth did not raise when all growth is finished")
        except Growth.DoesNotExist:
            pass

    def test_error_callback(self):
        self.skipTest("not tested")

    @patch("core.models.organisms.community.Growth.begin")
    def test_grow(self, begin_growth):
        self.set_instance_mocks()
        growth_finish_method = "core.models.organisms.community.Growth.finish"
        with patch(growth_finish_method, side_effect=self.raise_unfinished) as finish_growth:
            try:
                done = False
                done = self.instance.grow()
                self.fail("Growth.finish not patched")
            except DSProcessUnfinished:
                pass
            first_growth = self.instance.growth_set.first()
            self.assertFalse(done)
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertEqual(self.instance.current_growth.id, first_growth.id)  # first new Growth
            self.instance.call_begin_callback.assert_called_once_with("phase1", first_growth.input)
            self.assertFalse(self.instance.call_finish_callback.called)
            begin_growth.assert_called_once_with()

            self.set_instance_mocks()
            begin_growth.reset_mock()
            try:
                done = False
                done = self.instance.grow()
            except DSProcessUnfinished:
                pass
            self.assertFalse(done)
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertFalse(self.instance.call_begin_callback.called)
            self.assertFalse(self.instance.call_finish_callback.called)
            self.assertFalse(begin_growth.called)

        with patch(growth_finish_method, return_value=(first_growth.output, [])) as finish_growth:
            second_growth = self.instance.growth_set.last()
            with patch("core.models.organisms.community.Community.next_growth", return_value=second_growth):
                self.instance.grow()
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertEqual(self.instance.current_growth.id, second_growth.id)
            self.instance.call_finish_callback.assert_called_once_with("phase1", first_growth.output, [])
            self.instance.call_begin_callback.assert_called_once_with("phase2", second_growth.input)
            begin_growth.assert_called_once_with()

        self.set_instance_mocks()
        begin_growth.reset_mock()
        with patch(growth_finish_method, return_value=(second_growth.output, [])) as finish_growth:
            self.set_instance_mocks()
            with patch("core.models.organisms.community.Community.next_growth", side_effect=Growth.DoesNotExist):
                done = self.instance.grow()
            self.assertTrue(done)
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertEqual(self.instance.current_growth.id, second_growth.id)
            self.instance.call_finish_callback.assert_called_once_with("phase2", second_growth.output, [])
            self.assertIsInstance(self.instance.kernel, Collective)
            self.assertEqual(self.instance.kernel.id, second_growth.output.id)
            self.assertFalse(self.instance.call_begin_callback.called)
            self.assertFalse(begin_growth.called)

            second_growth.state = "Complete"
            second_growth.save()

        self.set_instance_mocks()
        with patch(growth_finish_method) as finish_growth:
            done = self.instance.grow()
        self.assertTrue(done)
        self.assertEqual(self.instance.growth_set.count(), 2)
        self.assertIsInstance(self.instance.current_growth, Growth)
        self.assertEqual(self.instance.current_growth.id, second_growth.id)
        self.assertFalse(self.instance.call_finish_callback.called)
        self.assertFalse(self.instance.call_begin_callback.called)
        self.assertFalse(begin_growth.called)
        self.assertFalse(finish_growth.called)

        self.skipTest("update test for sync flow")
        self.skipTest("test with states")

    def test_manifestation(self):
        self.skipTest("not tested")


class CommunityTestMixin(TestCase):

    def test_set_kernel(self):
        self.skipTest("not tested")

    def test_initial_input(self):
        self.skipTest("not tested")
