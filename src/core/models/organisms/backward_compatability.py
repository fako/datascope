from typing import List
from datetime import datetime


class SupressDatasetVersionFeatures:

    dataset_version = None

    tasks = {}
    task_results = {}
    derivatives = {}

    finished_at = None
    pending_at = None

    @classmethod
    def get_collection_model(cls):
        raise NotImplementedError()

    @classmethod
    def get_dataset_version_model(cls):
        raise NotImplementedError()

    def get_pending_tasks(self) -> List[str]:
        raise NotImplementedError()

    def get_property_dependencies(self) -> dict:
        return {}  # which assures updates of Documents won't trigger task invalidation

    def invalidate_task(self, task_name: str, current_time: datetime = None, commit: bool = False) -> None:
        raise NotImplementedError()

    def finish_processing(self, current_time: datetime = None, commit: bool = True):
        raise NotImplementedError()
