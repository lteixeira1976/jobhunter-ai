import requests
from datetime import datetime

from app.models.job import Job
from app.sources.base_source import JobSource


class GreenhouseSource(JobSource):

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self):
        self.board = "nubank"


    def search(self, keyword: str):

        url = f"{self.BASE_URL}/{self.board}/jobs"

        response = requests.get(url)

        if response.status_code != 200:
            return []


        data = response.json()

        jobs = []


        for item in data["jobs"]:

            title = item["title"]


            published_at = datetime.fromisoformat(
                item["updated_at"].replace("Z", "+00:00")
            )


            jobs.append(
                Job(
                    title=title,
                    company="Nubank",
                    url=item["absolute_url"],
                    location="",
                    source="Greenhouse",
                    description="",
                    published_at=published_at
                )
            )


        return jobs