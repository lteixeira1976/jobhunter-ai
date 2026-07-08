import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from app.models.job import Job
from app.sources.base_source import JobSource


class GupySource(JobSource):

    def __init__(self):
        self.name = "Gupy"

    def search(self, keyword):

        jobs = []

        query = keyword.replace(" ", "%20")

        url = f"https://portal.gupy.io/job-search/term={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            links = soup.find_all("a", href=True)

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                if "/jobs/" not in href:
                    continue

                title = link.text.strip()

                if not title:
                    title = keyword

                if href.startswith("/"):
                    job_url = f"https://portal.gupy.io{href}"
                else:
                    job_url = href

                jobs.append(
                    Job(
                        title=title,
                        company="Não identificado",
                        url=job_url,
                        location="Brasil",
                        source=self.name,
                        description=title,
                        published_at=datetime.now(timezone.utc)
                    )
                )

        except Exception as e:
            print(f"Erro Gupy Search: {e}")

        return jobs