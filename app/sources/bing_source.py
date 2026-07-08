import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.models.job import Job


class BingSource:

    def __init__(self):
        self.name = "Bing"

    def search(self, keyword):

        jobs = []

        query = (
            f'"{keyword}" '
            f'("vaga" OR "job" OR "careers" OR "trabalhe conosco") '
            f'Brasil'
        )

        url = "https://www.bing.com/search"

        params = {
            "q": query,
            "setlang": "pt-BR",
            "count": 20
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        blocked_domains = [
            "wikipedia.org",
            "britannica.com",
            "techcrunch.com",
            "techradar.com",
            "theverge.com",
            "reuters.com",
            "cnet.com",
            "cambridge.org",
            "wordreference.com",
            "spanishdict.com"
        ]

        job_domains = [
            "linkedin",
            "gupy",
            "indeed",
            "glassdoor",
            "greenhouse",
            "lever",
            "workday",
            "jobs",
            "careers",
            "carreiras",
            "vagas"
        ]

        blocked_titles = [
            "what is",
            "definition",
            "meaning",
            "wiki",
            "career advice",
            "salary guide"
        ]

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            results = soup.select("li.b_algo")

            print(f"Bing retornou {len(results)} resultados para: {keyword}")

            for item in results:

                link = item.find("a")

                if not link:
                    continue

                title = link.text.strip()
                job_url = link.get("href")

                print(f"DEBUG Bing: {title} | {job_url}")

                if not job_url:
                    continue

                parsed_url = urlparse(job_url)
                domain = parsed_url.netloc.lower()
                full_url = job_url.lower()
                title_lower = title.lower()

                if any(blocked in domain for blocked in blocked_domains):
                    continue

                if not any(allowed in full_url for allowed in job_domains):
                    continue

                if any(word in title_lower for word in blocked_titles):
                    continue

                description = ""

                snippet = item.find("p")

                if snippet:
                    description = snippet.text.strip()

                jobs.append(
                    Job(
                        title=title,
                        company="Não identificado",
                        url=job_url,
                        location="Brasil",
                        source=self.name,
                        description=description,
                        published_at=datetime.now(timezone.utc)
                    )
                )

        except Exception as e:
            print(f"Erro Bing Search: {e}")

        return jobs