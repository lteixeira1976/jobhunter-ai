from app.models.job import Job


class JobCollectorAgent:

    def __init__(self):
        self.name = "Job Collector Agent"


    def search(self, keyword):

        print(f"🔎 Buscando vagas para: {keyword}")

        jobs = [

            Job(
                title="Engineering Manager",
                company="Mercado Livre",
                url="https://careers.mercadolibre.com",
                location="Remoto",
                source="Career Site",
                description="""
                Liderança de times de engenharia,
                Java, APIs, arquitetura,
                AWS, SNS, SQS e mensageria.
                """
            ),

            Job(
                title="Technical Product Manager Senior",
                company="Mottu",
                url="https://mottu.com.br/carreiras",
                location="São Paulo",
                source="Career Site",
                description="""
                Gestão de produtos digitais,
                roadmap, tecnologia,
                APIs, métricas e integrações.
                """
            )

        ]

        return jobs