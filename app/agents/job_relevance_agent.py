from app.models.job import Job


class JobRelevanceAgent:

    def __init__(self):
        self.name = "Job Relevance Agent"

        self.priority_rules = {
            # Gestão de Engenharia / Tecnologia
            "software engineering manager": 100,
            "engineering manager": 100,
            "software development manager": 100,
            "development manager": 95,
            "tech manager": 100,
            "technology manager": 100,
            "technical manager": 100,
            "it manager": 90,
            "systems manager": 90,
            "gerente de engenharia de software": 100,
            "gerente de engenharia": 100,
            "gerente de tecnologia": 100,
            "gerente de desenvolvimento": 100,
            "gerente de sistemas": 95,
            "head of engineering": 100,

            # Coordenação / Liderança
            "engineering coordinator": 90,
            "technology coordinator": 90,
            "software development coordinator": 90,
            "coordenador de engenharia de software": 95,
            "coordenador de engenharia": 90,
            "coordenador de tecnologia": 90,
            "coordenador de sistemas": 85,
            "engineering lead manager": 95,
            "engineering lead": 85,
            "tech lead": 80,
            "technical lead": 80,
            "lead software engineer": 80,
            "líder de engenharia de software": 90,
            "lider de engenharia de software": 90,
            "líder de engenharia": 85,
            "lider de engenharia": 85,
            "líder técnico": 80,
            "lider técnico": 80,
            "tech coordinator": 85,

            # Produto Técnico
            "senior technical product manager": 95,
            "technical product manager": 95,
            "technology product manager": 90,
            "digital product manager": 85,
            "group product manager": 90,
            "product manager": 85,
            "delivery manager": 85,
            "platform manager": 85,

            # Engenharia Sênior
            "principal engineer": 80,
            "staff engineer": 75,
            "senior staff": 75,
            "senior software engineer": 60,
            "software engineer": 50,
        }

        # Termos que indicam engenharia fora de tecnologia
        self.non_tech_title_terms = [
            "mineração",
            "mineracao",
            "obras",
            "obra portuária",
            "obra portuaria",
            "infraestrutura",
            "construção civil",
            "construcao civil",
            "engenharia civil",
            "engenharia mecânica",
            "engenharia mecanica",
            "engenharia elétrica",
            "engenharia eletrica",
            "engenharia industrial",
            "engenharia de produção",
            "engenharia de producao",
            "engenharia e projetos",
            "projetos industriais",
            "saneamento",
            "ferrovia",
            "rodovia",
            "barragem",
            "óleo e gás",
            "oleo e gas",
        ]

        # Exceções explícitas que precisam aparecer no título
        self.tech_title_terms = [
            "software",
            "tecnologia",
            "technology",
            "tech",
            "sistemas",
            "systems",
            "digital",
            "dados",
            "data",
            "cloud",
            "platform",
            "plataforma",
            "ti",
            "it manager",
            "product",
            "produto digital",
        ]

    def evaluate(self, job: Job):
        title = (job.title or "").lower().strip()

        has_non_tech_term = any(
            term in title
            for term in self.non_tech_title_terms
        )

        has_explicit_tech_term = any(
            term in title
            for term in self.tech_title_terms
        )

        # Se o próprio título indica engenharia não tecnológica,
        # só será aceito caso também tenha contexto tech explícito no título.
        if has_non_tech_term and not has_explicit_tech_term:
            return {
                "relevant": False,
                "score": 0,
                "category": "engenharia não tecnológica"
            }

        matches = []

        for term, score in self.priority_rules.items():
            if term in title:
                matches.append(
                    {
                        "term": term,
                        "score": score
                    }
                )

        if not matches:
            return {
                "relevant": False,
                "score": 0,
                "category": "not relevant"
            }

        best_match = max(
            matches,
            key=lambda item: item["score"]
        )

        return {
            "relevant": True,
            "score": best_match["score"],
            "category": best_match["term"]
        }