import re
import unicodedata

from app.config.candidate_profile import CANDIDATE_PROFILE
from app.models.match_result import MatchResult


class MatchAgent:

    def __init__(self):
        self.criteria = {
            "people management": {
                "weight": 15,
                "terms": [
                    "people management",
                    "gestao de pessoas",
                    "lideranca de pessoas",
                    "people leadership",
                    "team leadership",
                    "lideranca de equipe",
                    "desenvolvimento de pessoas",
                    "career development",
                    "mentoria",
                    "coaching",
                ],
            },

            "engineering management": {
                "weight": 15,
                "terms": [
                    "engineering management",
                    "gestao de engenharia",
                    "engineering manager",
                    "tech manager",
                    "technology manager",
                    "gerente de engenharia",
                    "gerente de tecnologia",
                    "software engineering",
                    "lideranca tecnica",
                    "technical leadership",
                ],
            },

            "stakeholders": {
                "weight": 8,
                "terms": [
                    "stakeholder",
                    "stakeholders",
                    "areas de negocio",
                    "business partners",
                    "executive leadership",
                    "liderancas executivas",
                    "cross-functional",
                    "multidisciplinar",
                ],
            },

            "product strategy": {
                "weight": 12,
                "terms": [
                    "product strategy",
                    "estrategia de produto",
                    "product management",
                    "gestao de produto",
                    "product discovery",
                    "discovery",
                    "roadmap",
                    "backlog",
                    "mvp",
                    "produto digital",
                    "digital product",
                    "priorizacao",
                    "prioritization",
                ],
            },

            "architecture": {
                "weight": 12,
                "terms": [
                    "software architecture",
                    "arquitetura de software",
                    "solution architecture",
                    "arquitetura de solucao",
                    "distributed systems",
                    "sistemas distribuidos",
                    "microservices",
                    "microsservicos",
                    "event driven",
                    "orientada a eventos",
                    "apis",
                    "api",
                    "integration",
                    "integracoes",
                ],
            },

            "cloud and platforms": {
                "weight": 8,
                "terms": [
                    "aws",
                    "amazon web services",
                    "azure",
                    "gcp",
                    "cloud",
                    "kafka",
                    "rabbitmq",
                    "sns",
                    "sqs",
                    "lambda",
                    "platform",
                    "plataforma",
                ],
            },

            "delivery and metrics": {
                "weight": 8,
                "terms": [
                    "lead time",
                    "cycle time",
                    "throughput",
                    "deploy frequency",
                    "mttr",
                    "sla",
                    "slo",
                    "availability",
                    "disponibilidade",
                    "kpi",
                    "kpis",
                    "okr",
                    "okrs",
                    "metrics",
                    "metricas",
                    "data driven",
                    "orientado a dados",
                ],
            },

            "agile and devops": {
                "weight": 6,
                "terms": [
                    "agile",
                    "agil",
                    "scrum",
                    "kanban",
                    "devops",
                    "devsecops",
                    "ci/cd",
                    "continuous delivery",
                    "entrega continua",
                    "observability",
                    "observabilidade",
                ],
            },

            "artificial intelligence": {
                "weight": 4,
                "terms": [
                    "artificial intelligence",
                    "inteligencia artificial",
                    "generative ai",
                    "ia generativa",
                    "machine learning",
                    "llm",
                    "automation",
                    "automacao",
                ],
            },
        }

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

    @classmethod
    def contains_term(cls, text, term):
        normalized_text = cls.normalize(text)
        normalized_term = cls.normalize(term)

        pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"

        return re.search(pattern, normalized_text) is not None

    def calculate_role_score(self, title):
        title = self.normalize(title)

        tier_scores = {
            "tier_1": 12,
            "tier_2": 9,
            "tier_3": 5,
        }

        for tier_name, tier_config in (
            CANDIDATE_PROFILE["target_roles"].items()
        ):
            for role in tier_config["roles"]:
                if self.contains_term(title, role):
                    return tier_scores.get(tier_name, 0), tier_name

        return 0, None

    def calculate(self, job):
        title = job.title or ""
        description = job.description or ""
        full_text = f"{title} {description}"

        total_score = 0
        strengths = []
        gaps = []

        role_score, role_tier = self.calculate_role_score(title)
        total_score += role_score

        if role_tier:
            strengths.append(f"cargo {role_tier}")

        for criterion, config in self.criteria.items():
            found_terms = [
                term
                for term in config["terms"]
                if self.contains_term(full_text, term)
            ]

            if found_terms:
                total_score += config["weight"]
                strengths.append(criterion)
            else:
                gaps.append(criterion)

        score = min(100, total_score)

        if score >= 70:
            recommendation = "APLICAR"
            priority = "ALTA"

        elif score >= 45:
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
            priority=priority,
        )