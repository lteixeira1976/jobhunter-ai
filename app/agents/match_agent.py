from app.models.profile import luciano_profile
from app.models.match_result import MatchResult


class MatchAgent:


    def calculate(self, job):

        text = (
            job.title +
            " " +
            job.description
        ).lower()


        strengths = []
        gaps = []


        for skill in luciano_profile.skills:

            if skill.lower() in text:
                strengths.append(skill)


        total_skills = len(luciano_profile.skills)

        score = int(
            (len(strengths) / total_skills) * 100
        )


        if score >= 70:

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

            strengths=strengths,

            gaps=gaps,

            recommendation=recommendation,

            priority=priority
        )