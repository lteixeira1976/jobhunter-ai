from app.sources.greenhouse_source import GreenhouseSource
from app.sources.gupy_source import GupySource


class JobCollectorAgent:

    def __init__(self):

        self.sources = [
            GreenhouseSource(),
            GupySource()
        ]

    def search(self, keyword):

        print(f"🔎 Buscando vagas para: {keyword}")

        jobs = []

        for source in self.sources:

            try:
                jobs.extend(source.search(keyword))

            except Exception as e:
                print(f"Erro em {source.__class__.__name__}: {e}")

        unique_jobs = {}

        for job in jobs:

            if job.url:
                unique_jobs[job.url] = job

        return list(unique_jobs.values())