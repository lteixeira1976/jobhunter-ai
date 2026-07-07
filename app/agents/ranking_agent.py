class RankingAgent:


    def rank(self, matches):

        for item in matches:

            relevance_score = item["relevance"]["score"]

            match_score = item["result"].score


            item["ranking_score"] = (
                relevance_score * 0.6
                +
                match_score * 0.4
            )


        return sorted(
            matches,
            key=lambda x: x["ranking_score"],
            reverse=True
        )