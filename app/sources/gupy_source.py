import requests
from datetime import datetime
from typing import List

from app.models.job import Job
from app.sources.base_source import JobSource


class GupySource(JobSource):

    BASE_URL = "https://employability-portal.gupy.io/api/v1/jobs"

    def __init__(self, page_limit: int = 50):
        self.page_limit = page_limit

    def search(self, keyword: str) -> List[Job]:
        jobs: List[Job] = []
        offset = 0

        while True:
            params = {
                "jobName": keyword,
                "limit": self.page_limit,
                "offset": offset,
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=30,
                )
                response.raise_for_status()
            except requests.RequestException as error:
                print(f"Erro ao consultar Gupy: {error}")
                break

            payload = response.json()
            items = payload.get("data", [])
            pagination = payload.get("pagination", {})

            if not items:
                break

            for item in items:
                published_at = None
                published_date = item.get("publishedDate")

                if published_date:
                    try:
                        published_at = datetime.fromisoformat(
                            published_date.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                city = item.get("city", "")
                state = item.get("state", "")
                country = item.get("country", "")

                location = ", ".join(
                    part for part in [city, state, country] if part
                )

                jobs.append(
                    Job(
                        title=item.get("name", ""),
                        company=item.get("careerPageName", ""),
                        url=item.get("jobUrl", ""),
                        location=location,
                        source="Gupy",
                        description=item.get("description", ""),
                        published_at=published_at,
                    )
                )

            total = pagination.get("total", 0)
            offset += self.page_limit

            if offset >= total:
                break

        return jobs