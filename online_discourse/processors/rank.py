from core.processors.rank import RankProcessor


class OnlineDiscourseRankProcessor(RankProcessor):

    contextual_features = ["keyword_count"]

    @staticmethod
    def argument_score(individual):
        return individual.get("argument_score", 0.0)

    @staticmethod
    def keyword_count(individual, context):
        if not individual.get("word_count", {}):
            return 1
        else:
            return 0
