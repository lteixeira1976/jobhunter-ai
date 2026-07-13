from app.sources.greenhouse_source import GreenhouseSource
from app.sources.gupy_source import GupySource


class JobCollectorAgent:

    def __init__(self):
        self.sources = [
            GreenhouseSource(),
            GupySource(),
        ]

    def search(self, keyword):
        jobs = []

        for source in self.sources:
            try:
                jobs.extend(source.search(keyword))

            except Exception as error:
                print(
                    f"⚠️ Erro na fonte "
                    f"{source.__class__.__name__}: {error}"
                )

        unique_jobs = {}

        for job in jobs:
            if job.url:
                key = job.url.strip().lower()
            else:
                key = (
                    f"{job.company or ''}-"
                    f"{job.title or ''}"
                ).strip().lower()

            unique_jobs[key] = job

        return list(unique_jobs.values())