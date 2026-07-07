from app.sources.greenhouse_source import GreenhouseSource


class JobCollectorAgent:

    def __init__(self):

        self.sources = [
            GreenhouseSource()
        ]

    def search(self, keyword):

        print(f"🔎 Buscando vagas para: {keyword}")

        jobs = []

        for source in self.sources:
            jobs.extend(source.search(keyword))

        return jobs