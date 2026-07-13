import re

from app.models.match_result import MatchResult
from app.models.skill_priority import SKILL_PRIORITY
from app.models.skill_aliases import SKILL_ALIASES


class MatchAgent:

    @staticmethod
    def contains_term(text: str, term: str) -> bool:
        pattern = rf"(?<!\w){re.escape(term.lower())}(?!\w)"
        return re.search(pattern, text.lower()) is not None

    def calculate(self, job):

        text = f"{job.title} {job.description}".lower()

        strengths = []
        gaps = []
        total_points = 0
        max_points = 100

        for skill, weight in SKILL_PRIORITY.items():

            aliases = SKILL_ALIASES.get(skill, [skill])

            found = any(
                self.contains_term(text, alias)
                for alias in aliases
            )

            if found:
                total_points += weight
                strengths.append(skill)

        score = min(
            100,
            int((total_points / max_points) * 100)
        )

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
            strengths=sorted(set(strengths)),
            gaps=gaps,
            recommendation=recommendation,
            priority=priority
        )