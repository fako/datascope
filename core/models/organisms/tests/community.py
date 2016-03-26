from __future__ import unicode_literals

from django.test import TestCase

from mock import Mock, patch

from core.models.organisms import Individual, Collective, Growth, Community, Organism
from core.models.organisms.community import CommunityState
from core.models.organisms.growth import GrowthState
from core.tests.mocks.community import CommunityMock
from core.tests.mocks.http import HttpResourceMock
from core.exceptions import DSProcessUnfinished, DSProcessError


class CommunityTestMixin(TestCase):

    def test_initial_input(self):
        if not issubclass(self.instance.__class__, Community):
            self.skipTest('CommunityTestMixin expected an self.instance that is a Community subclass')
        initial_input = self.instance.initial_input()
        self.assertIsInstance(initial_input, Organism)


class TestCommunityMock(CommunityTestMixin):

    fixtures = ["test-community"]

    def setUp(self):
        super(TestCommunityMock, self).setUp()
        self.instance = CommunityMock.objects.get(id=1)
        self.incomplete = CommunityMock.objects.get(id=2)
        self.complete = CommunityMock.objects.get(id=3)
        self.error = CommunityMock.objects.get(id=4)

    def raise_unfinished(self, result):
        raise DSProcessUnfinished("Raised for test")

    def set_callback_mocks(self):
        self.instance.call_begin_callback = Mock()
        self.instance.call_finish_callback = Mock()
        self.error.error_phase1_unreachable = Mock(return_value=True)
        self.error.error_phase1_not_found = Mock(return_value=False)

    def test_get_or_create_by_input(self):
        community, created = CommunityMock.get_or_create_by_input("test", setting1="const", illegal="please")
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertFalse(created)
        self.assertEqual(community.config.setting1, "const")
        self.assertFalse(hasattr(community.config, "illegal"))
        community, created = CommunityMock.get_or_create_by_input("test", **{"$setting2": "variable"})
        self.assertIsNotNone(community)
        self.assertTrue(created)
        self.assertTrue(hasattr(community.config, "$setting2"))

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
        self.assertTrue(growth1.config.test_flag)
        self.assertTrue(growth2.config.test_flag)
        self.assertEqual(growth1.output.id, growth2.input.id)
        self.assertEqual(growth1.contribute, "ExtractProcessor.extract_from_resource")
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

    @patch("core.models.CommunityMock.set_kernel")
    def test_erroneous_community(self, set_kernel):
        empty_output = Collective.objects.get(id=2)
        full_output = Collective.objects.get(id=3)
        self.set_callback_mocks()
        try:
            self.error.grow()
            self.fail("Community did not raise error when dealing with errors and empty results.")
        except DSProcessError:
            pass
        self.assertEqual(self.error.state, CommunityState.ABORTED)
        self.error.error_phase1_unreachable.assert_called_once_with(
            list(self.error.current_growth.resources.filter(status=502)),
            empty_output
        )
        self.error.error_phase1_not_found.assert_called_once_with(
            list(self.error.current_growth.resources.filter(status=404)),
            empty_output
        )
        set_kernel.assert_not_called()

        self.set_callback_mocks()
        self.error.state = CommunityState.ASYNC
        self.error.save()
        self.error.current_growth.state = GrowthState.COMPLETE  # bypass growth logic
        self.error.current_growth.output = full_output
        self.error.current_growth.save()

        try:
            self.error.grow()
            self.fail("Community did not raise error when dealing with fatal errors in results.")
        except DSProcessError:
            pass
        self.assertEqual(self.error.state, CommunityState.ABORTED)
        self.error.error_phase1_unreachable.assert_called_once_with(
            list(self.error.current_growth.resources.filter(status=502)),
            full_output
        )
        self.error.error_phase1_not_found.assert_called_once_with(
            list(self.error.current_growth.resources.filter(status=404)),
            full_output
        )
        set_kernel.assert_not_called()

        self.set_callback_mocks()
        self.error.state = CommunityState.ASYNC
        self.error.save()
        self.error.current_growth.state = GrowthState.COMPLETE  # bypass growth logic
        self.error.current_growth.save()
        error_resource = HttpResourceMock.objects.get(status=404)
        error_resource.retainer = None
        error_resource.save()

        try:
            self.error.grow()
        except DSProcessError:
            self.fail("Community raised an error when dealing with non-fatal errors in results")
        self.assertEqual(self.error.state, CommunityState.READY)
        self.error.error_phase1_unreachable.assert_called_once_with(
            list(self.error.current_growth.resources.filter(status=502)),
            full_output
        )
        self.assertFalse(self.error.error_phase1_not_found.called)
        self.assertEqual(set_kernel.call_count, 1)

        self.set_callback_mocks()
        self.error.state = CommunityState.ASYNC
        self.error.COMMUNITY_SPIRIT["phase1"]["errors"] = None
        self.error.save()
        self.error.current_growth.state = GrowthState.COMPLETE  # bypass growth logic
        self.error.current_growth.save()
        set_kernel.reset_mock()

        try:
            self.error.grow()
        except DSProcessError:
            self.fail("Community raised an error with no error configuration present")
        self.assertEqual(self.error.state, CommunityState.READY)
        self.assertFalse(self.error.error_phase1_unreachable.called)
        self.assertFalse(self.error.error_phase1_not_found.called)
        self.assertEqual(set_kernel.call_count, 1)


    @patch("core.models.organisms.community.Growth.begin")
    def test_grow_async(self, begin_growth):
        self.set_callback_mocks()
        self.assertEqual(self.instance.state, CommunityState.NEW)
        growth_finish_method = "core.models.organisms.community.Growth.finish"
        with patch(growth_finish_method, side_effect=self.raise_unfinished) as finish_growth:
            done = False
            try:
                done = self.instance.grow()  # start growth
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
            self.assertEqual(self.instance.state, CommunityState.ASYNC)

            self.set_callback_mocks()
            begin_growth.reset_mock()
            try:
                done = False
                done = self.instance.grow()  # continue growth in background
            except DSProcessUnfinished:
                pass
            self.assertFalse(done)
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertFalse(self.instance.call_begin_callback.called)
            self.assertFalse(self.instance.call_finish_callback.called)
            self.assertFalse(begin_growth.called)
            self.assertEqual(self.instance.state, CommunityState.ASYNC)

        with patch(growth_finish_method, return_value=(first_growth.output, [])) as finish_growth:
            second_growth = self.instance.growth_set.last()
            with patch("core.models.organisms.community.Community.next_growth", return_value=second_growth):
                try:
                    self.instance.grow()  # first stage done, start second stage
                    self.fail("Unfinished community didn't raise any exception.")
                except DSProcessUnfinished:
                    pass
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertEqual(self.instance.current_growth.id, second_growth.id)
            self.instance.call_finish_callback.assert_called_once_with("phase1", first_growth.output, [])
            self.instance.call_begin_callback.assert_called_once_with("phase2", second_growth.input)
            begin_growth.assert_called_once_with()
            self.assertEqual(self.instance.state, CommunityState.ASYNC)

        self.set_callback_mocks()
        begin_growth.reset_mock()
        with patch(growth_finish_method, return_value=(second_growth.output, [])) as finish_growth:
            self.set_callback_mocks()
            with patch("core.models.organisms.community.Community.next_growth", side_effect=Growth.DoesNotExist):
                done = self.instance.grow()  # finish growth
            self.assertTrue(done)
            self.assertEqual(self.instance.growth_set.count(), 2)
            self.assertIsInstance(self.instance.current_growth, Growth)
            self.assertEqual(self.instance.current_growth.id, second_growth.id)
            self.instance.call_finish_callback.assert_called_once_with("phase2", second_growth.output, [])
            self.assertIsInstance(self.instance.kernel, Collective)
            self.assertEqual(self.instance.kernel.id, second_growth.output.id)
            self.assertFalse(self.instance.call_begin_callback.called)
            self.assertFalse(begin_growth.called)
            self.assertEqual(self.instance.state, CommunityState.READY)

            second_growth.state = "Complete"
            second_growth.save()

        self.set_callback_mocks()
        with patch(growth_finish_method) as finish_growth:
            done = self.instance.grow()  # don't grow further
        self.assertTrue(done)
        self.assertEqual(self.instance.growth_set.count(), 2)
        self.assertIsInstance(self.instance.current_growth, Growth)
        self.assertEqual(self.instance.current_growth.id, second_growth.id)
        self.assertFalse(self.instance.call_finish_callback.called)
        self.assertFalse(self.instance.call_begin_callback.called)
        self.assertFalse(begin_growth.called)
        self.assertFalse(finish_growth.called)
        self.assertEqual(self.instance.state, CommunityState.READY)

    @patch('core.processors.resources.HttpResourceProcessor.get_link', return_value=HttpResourceMock())
    def test_grow_sync(self, get_link):
        self.instance.config.async = False
        self.set_callback_mocks()
        self.assertEqual(self.instance.state, CommunityState.NEW)
        done = self.instance.grow()
        self.assertTrue(done)
        self.assertEqual(self.instance.growth_set.filter(state=GrowthState.COMPLETE).count(), 2)
        self.assertIsInstance(self.instance.current_growth, Growth)
        self.assertEqual(self.instance.current_growth.id, self.instance.growth_set.last().id)
        self.assertEqual(self.instance.state, CommunityState.READY)

    def test_manifestation(self):
        self.complete.config.include_odd = True
        manifestation = self.complete.manifestation
        self.assertEqual(len(manifestation), 2)
        self.complete.config.include_even = True
        manifestation = self.complete.manifestation
        self.assertEqual(len(manifestation), 3)
        self.complete.config.include_odd = False
        manifestation = self.complete.manifestation
        self.assertEqual(len(manifestation), 1)
        self.complete.config.include_even = False
        manifestation = self.complete.manifestation
        self.assertEqual(len(manifestation), 0)
