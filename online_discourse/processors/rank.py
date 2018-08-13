from core.processors.rank import RankProcessor


class OnlineDiscourseRankProcessor(RankProcessor):

    @staticmethod
    def argument_score(individual):
        return individual.get("argument_score", 0.0)
