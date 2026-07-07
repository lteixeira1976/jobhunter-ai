from dataclasses import dataclass
from datetime import datetime


@dataclass
class Job:

    title: str
    company: str
    url: str
    location: str
    source: str
    description: str
    published_at: datetime = None