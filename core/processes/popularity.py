from base import Process, Retrieve
from decimal import Decimal


# TODO: This is a naive way of doing it. Way better to have a MergeProcess to merge details with listings.
class YouTubePopularityComparison(Process):

    def process(self):

        subject_a = self.config.a
        subject_b = self.config.b

        retrieve_a = Retrieve()
        retrieve_a.execute(subject_a, **{
            "_link": "YouTubeSearch"
        })
        video_a = retrieve_a.rsl[0] if retrieve_a.rsl else None

        retrieve_b = Retrieve()
        retrieve_b.execute(subject_b, **{
            "_link": "YouTubeSearch"
        })
        video_b = retrieve_b.rsl[0] if retrieve_b.rsl else None

        if not video_a or not video_b:
            self.rsl = None
            return

        popularity_a = Retrieve()
        popularity_a.execute(video_a['vid'], **{
            "_link": "YouTubeDetails"
        })

        popularity_b = Retrieve()
        popularity_b.execute(video_b['vid'], **{
            "_link": "YouTubeDetails"
        })

        self.rsl = {
            "viewCount": Decimal(popularity_a.rsl[0]['viewCount']) / Decimal(popularity_b.rsl[0]['viewCount'])
        }

    class Meta:
        app_label = "core"
        proxy = True
