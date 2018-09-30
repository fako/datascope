from core.processors.rank import RankProcessor


class OnlineDiscourseRankProcessor(RankProcessor):

    contextual_features = ["keyword_count"]

    def get_text(self, document):
        paragraph_groups = document.get("paragraph_groups", [])
        text = ""
        for paragraph_group in paragraph_groups:
            text += " ".join(paragraph_group) + " "
        return text

    def default_ranking(self, individuals):
        individuals = list(individuals)  # TODO: optimize memory use
        argument_score_rank = self.feature_frame.data["argument_score"]
        keyword_count_rank = self.feature_frame.get_feature_series(
            "keyword_count", self.keyword_count,
            content_callable=lambda: individuals, context=self.config.to_dict()
        )
        ranking_series = argument_score_rank.add(keyword_count_rank)
        ranking_series = ranking_series.sort_values(ascending=False)[:self.config.result_size]
        return self.get_ranking_results(ranking_series, individuals, [argument_score_rank, keyword_count_rank])

    @staticmethod
    def argument_score(individual):
        return individual.get("argument_score", 0.0)

    @staticmethod
    def keyword_count(individual, context):
        # Early exit if context does not require any calculation
        keywords = context.get("keywords", [])
        word_count = individual.get("word_count", {})
        if not keywords or not word_count:
            return 0
        word_total = sum(word_count.values())
        # The actual keyword_count calculation
        return sum([word_count.get(keyword, 0) / word_total for keyword in keywords], 0)
