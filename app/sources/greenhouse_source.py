import requests
from datetime import datetime

from app.models.job import Job
from app.sources.base_source import JobSource


class GreenhouseSource(JobSource):

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self):
        self.boards = [
            {
                "board": "nubank",
                "company": "Nubank"
            }
        ]

    def search(self, keyword: str):

        jobs = []

        for board_config in self.boards:
            board = board_config["board"]
            company = board_config["company"]

            url = f"{self.BASE_URL}/{board}/jobs"

            response = requests.get(url)

            if response.status_code != 200:
                continue

            data = response.json()

            for item in data["jobs"]:

                title = item["title"]

                if keyword.lower() not in title.lower():
                    continue

                published_at = datetime.fromisoformat(
                    item["updated_at"].replace("Z", "+00:00")
                )

                jobs.append(
                    Job(
                        title=title,
                        company=company,
                        url=item["absolute_url"],
                        location="",
                        source="Greenhouse",
                        description="",
                        published_at=published_at
                    )
                )

        return jobs