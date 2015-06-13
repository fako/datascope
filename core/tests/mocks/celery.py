from __future__ import unicode_literals, absolute_import, print_function, division

from mock import Mock

from celery import Task
from celery.result import AsyncResult, states as CeleryState


MockTaskChain = Mock(spec=Task, id="result-id")
MockTask = Mock(spec=Task, id="result-id", return_value=MockTaskChain)
MockTask.attach_mock(MockTask, "s")
MockTask.attach_mock(MockTask, "delay")

MockAsyncResultPartial = Mock(spec=AsyncResult)
MockAsyncResultPartial.attach_mock(Mock(return_value=True), "ready")
MockAsyncResultPartial.status = CeleryState.SUCCESS
MockAsyncResultPartial.result = ([1, 2, 3], [4, 5],)

MockAsyncResultSuccess = Mock(spec=AsyncResult)
MockAsyncResultSuccess.attach_mock(Mock(return_value=True), "ready")
MockAsyncResultSuccess.status = CeleryState.SUCCESS
MockAsyncResultSuccess.result = ([1, 2, 3], [],)

MockAsyncResultError = Mock(spec=AsyncResult)
MockAsyncResultError.attach_mock(Mock(return_value=True), "ready")
MockAsyncResultError.status = CeleryState.FAILURE

MockAsyncResultWaiting = Mock(spec=AsyncResult)
MockAsyncResultWaiting.attach_mock(Mock(return_value=False), "ready")