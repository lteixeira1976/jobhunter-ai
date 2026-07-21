import re
import unicodedata

from app.config.candidate_resume import RESUME


class CVOptimizer:

    def __init__(self):
        self.resume = RESUME

    @staticmethod
    def normalize(text):
        if not text:
            return ""

        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            character
            for character in text
            if not unicodedata.combining(character)
        )

        return re.sub(r"\s+", " ", text.lower()).strip()

    def optimize(self, job):
        description = self.normalize(job.description)
        title = job.title or ""

        matched_skills = []
        unmatched_skills = []

        for skill in self.resume["skills"]:
            normalized_skill = self.normalize(skill)

            if normalized_skill in description:
                matched_skills.append(skill)
            else:
                unmatched_skills.append(skill)

        ordered_skills = matched_skills + unmatched_skills

        optimized_summary = (
            f"Líder de Tecnologia com experiência aderente à posição "
            f"de {title}, atuando na conexão entre Engenharia, Produto "
            f"e Negócio. Possuo experiência em liderança de squads, "
            f"produtos digitais, arquitetura de software, APIs, "
            f"microsserviços, cloud e evolução de plataformas críticas."
        )

        if matched_skills:
            optimized_summary += (
                " Para esta oportunidade, destacam-se competências como "
                + ", ".join(matched_skills[:8])
                + "."
            )

        return {
            "job_title": title,
            "company": job.company,
            "summary": optimized_summary,
            "matched_skills": matched_skills,
            "ordered_skills": ordered_skills,
        }