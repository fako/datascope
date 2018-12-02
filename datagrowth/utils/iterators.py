import math
from itertools import islice
from tqdm import tqdm


def ibatch(iterable, batch_size, progress_bar=False, total=None):

    # Setup a progress bar if requested
    if progress_bar and not total:
        progress_bar = tqdm()
    elif progress_bar and total:
        batches = int(math.floor(total / batch_size))
        rest = total % batch_size
        if rest:
            batches += 1
        progress_bar = tqdm(total=batches)

    # The actual batch iterator
    it = iter(iterable)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            if progress_bar:
                progress_bar.close()
            return
        if progress_bar:
            progress_bar.update(1)
        yield batch
