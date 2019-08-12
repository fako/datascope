import os
from tqdm import tqdm

from django.core.serializers import serialize, deserialize

from datagrowth import settings as datagrowth_settings
from datagrowth.utils.iterators import ibatch


def get_model_path(app_label, model_type=""):
    return os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, app_label, model_type).rstrip(os.sep)


def get_media_path(app_label, media_type="", absolute=True):
    if absolute:
        return os.path.join(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, app_label, media_type).rstrip(os.sep)
    else:
        return os.path.join(app_label, media_type).rstrip(os.sep)


def get_dumps_path(model):
    return os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, model._meta.app_label, "dumps", model.get_name())


def queryset_to_disk(queryset, dump_file, batch_size=100):
    count = queryset.all().count()
    batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size, progress_bar=True, total=count)
    for batch in batch_iterator:
        batch_data = serialize("json", batch, use_natural_foreign_keys=True)
        dump_file.writelines([batch_data + "\n"])


def object_to_disk(object, dump_file):
    batch_data = serialize("json", [object], use_natural_foreign_keys=True)
    dump_file.write(batch_data + "\n")


def objects_from_disk(dump_file):
    batch_count = 0
    for _ in dump_file.readlines():
        batch_count += 1
    dump_file.seek(0)
    for line in tqdm(dump_file, total=batch_count):
        yield [wrapper.object for wrapper in deserialize("json", line)]
