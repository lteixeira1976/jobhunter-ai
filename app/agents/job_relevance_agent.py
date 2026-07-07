from app.models.job import Job


class JobRelevanceAgent:

    def __init__(self):

        self.name = "Job Relevance Agent"

        self.priority_rules = {

            # 🥇 Gestão de Engenharia / Tecnologia
            "engineering manager": 100,
            "software engineering manager": 100,
            "tech manager": 100,
            "technology manager": 100,
            "technical manager": 100,
            "gerente de engenharia": 100,
            "gerente de tecnologia": 100,
            "head of engineering": 100,
            "engineering lead manager": 95,

            # 🥈 Produto Técnico
            "senior technical product manager": 95,
            "technical product manager": 95,
            "technology product manager": 90,
            "product manager": 85,

            # 🥉 Liderança Técnica
            "tech lead": 80,
            "lead software engineer": 80,
            "principal engineer": 80,
            "staff engineer": 75,
            "senior staff": 75,

            # Engenharia Sênior
            "senior software engineer": 60,
            "software engineer": 50

        }


    def evaluate(self, job: Job):

        title = job.title.lower()

        matches = []

        for term, score in self.priority_rules.items():

            if term in title:

                matches.append(
                    {
                        "term": term,
                        "score": score
                    }
                )


        if matches:

            best_match = max(
                matches,
                key=lambda x: x["score"]
            )

            return {
                "relevant": True,
                "score": best_match["score"],
                "category": best_match["term"]
            }


        return {
            "relevant": False,
            "score": 0,
            "category": "not relevant"
        }