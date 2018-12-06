from core.processors.rank import RankProcessor
from datagrowth.configuration import ConfigurationNotFoundError


class OnlineDiscourseRankProcessor(RankProcessor):

    contextual_features = ["keyword_count"]

    @staticmethod
    def get_text(document):
        paragraph_groups = document.get("paragraph_groups", [])
        text = ""
        for paragraph_group in paragraph_groups:
            paragraphs = [paragraph for paragraph in paragraph_group if isinstance(paragraph, str)]
            text += " ".join(paragraphs) + " "
        return text

    def default_ranking(self, query_set):
        argument_score_rank = self.feature_frame.data["argument_score"]
        argument_score_max = argument_score_rank.max()
        argument_score_rank /= argument_score_max
        try:  # TODO: replace try with .get from config
            keywords = self.config.keywords
        except ConfigurationNotFoundError:
            keywords = []
        keyword_params = {
            keyword: 1
            for keyword in keywords
        }
        keyword_count_rank = self.text_frame.score_by_params(keyword_params)
        if keyword_count_rank is None:
            ranking_series = argument_score_rank.fillna(0).sort_values(ascending=False)
            return self.get_ranking_results(ranking_series, query_set, [argument_score_rank])
        keyword_count_rank.name = "keywords"
        keyword_max = keyword_count_rank.max()
        keyword_count_rank /= keyword_max
        ranking_series = argument_score_rank.add(keyword_count_rank)
        ranking_series = ranking_series.fillna(0).sort_values(ascending=False)
        return self.get_ranking_results(ranking_series, query_set, [argument_score_rank, keyword_count_rank])

    @staticmethod
    def argument_score(individual):
        return individual.get("argument_score", 0.0)
