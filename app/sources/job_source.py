from app.sources.base_source import JobSource
from app.models.job import Job


class MockJobSource(JobSource):


    def search(self, keyword):

        return [

            Job(
                title="Engineering Manager",
                company="Mercado Livre",
                url="https://careers.mercadolibre.com",
                location="Remoto",
                source="Career Site",
                description="""
                Liderança de times de engenharia,
                Java, APIs, arquitetura,
                AWS, mensageria e produtos digitais.
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
                tecnologia, roadmap, APIs,
                métricas e integração.
                """
            )
        ]