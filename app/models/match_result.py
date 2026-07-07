from dataclasses import dataclass
from typing import List


@dataclass
class MatchResult:

    score: int

    strengths: List[str]

    gaps: List[str]

    recommendation: str

    priority: str
    