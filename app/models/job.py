from dataclasses import dataclass


@dataclass
class Job:

    title: str
    company: str
    url: str
    location: str
    source: str
    description: str