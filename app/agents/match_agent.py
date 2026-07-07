from app.models.match_result import MatchResult
from app.models.skill_priority import SKILL_PRIORITY
from app.models.skill_aliases import SKILL_ALIASES


class MatchAgent:


    def calculate(self, job):

        text = (
            job.title +
            " " +
            job.description
        ).lower()


        strengths = []
        gaps = []


        total_points = 0

        max_points = 100


        for skill, weight in SKILL_PRIORITY.items():

            aliases = SKILL_ALIASES.get(
                skill,
                [skill]
            )


            found = False


            for alias in aliases:

                if alias.lower() in text:

                    found = True
                    break


            if found:

                total_points += weight
                strengths.append(skill)



        score = int(
            (total_points / max_points) * 100
        )
        if score > 100:
            score = 100


        if score >= 60:

            recommendation = "APLICAR"
            priority = "ALTA"


        elif score >= 40:

            recommendation = "AVALIAR"
            priority = "MEDIA"


        else:

            recommendation = "BAIXA PRIORIDADE"
            priority = "BAIXA"



        return MatchResult(

            score=score,

            strengths=list(set(strengths)),

            gaps=gaps,

            recommendation=recommendation,

            priority=priority

        )