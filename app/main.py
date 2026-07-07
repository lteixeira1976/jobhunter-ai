from datetime import datetime

from app.agents.job_collector import JobCollectorAgent
from app.agents.match_agent import MatchAgent
from app.database.database import JobDatabase


def main():

    print("=" * 50)
    print("🚀 JobHunter AI iniciado")
    print("=" * 50)
    print(f"Data: {datetime.now()}")
    print()

    collector = JobCollectorAgent()
    matcher = MatchAgent()
    database = JobDatabase()

    jobs = collector.search(
        "Technical Product Manager Senior"
    )

    print(f"Vagas encontradas: {len(jobs)}")

    for job in jobs:

        result = matcher.calculate(job)

        print()
        print("-----------------------")
        print(f"Empresa: {job.company}")
        print(f"Cargo: {job.title}")
        print(f"Match: {result.score}%")

        database.save(
            job,
            result.score
        )

    print()
    print("✅ Vagas salvas no banco")


if __name__ == "__main__":
    main()
    