from datetime import datetime, timezone, timedelta

from app.agents.job_collector import JobCollectorAgent
from app.agents.match_agent import MatchAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.job_relevance_agent import JobRelevanceAgent

from app.config.search_config import SEARCH_CONFIG
from app.database.database import JobDatabase

from app.services.job_detail_service import JobDetailService
from app.services.job_filter_service import JobFilterService


def build_search_terms():
    search_terms = []

    for position_group in SEARCH_CONFIG["positions"].values():
        search_terms.extend(position_group)

    return list(dict.fromkeys(search_terms))


def main():
    brasil_timezone = timezone(timedelta(hours=-3))
    current_time = datetime.now(brasil_timezone)

    collector = JobCollectorAgent()
    matcher = MatchAgent()
    ranking = RankingAgent()
    relevance = JobRelevanceAgent()

    database = JobDatabase()
    detail_service = JobDetailService()
    filter_service = JobFilterService()

    search_terms = build_search_terms()
    days_filter = SEARCH_CONFIG["days"]

    print("=" * 60)
    print("🚀 JOBHUNTER AI")
    print("=" * 60)
    print(
        f"Execução: {current_time.strftime('%d/%m/%Y %H:%M')}"
    )
    print(
        f"Período analisado: últimos {days_filter} dias"
    )
    print()

    jobs = []

    for term in search_terms:
        results = collector.search(term)
        jobs.extend(results)

    total_collected = len(jobs)

    unique_jobs = {}

    for job in jobs:
        if job.url:
            key = job.url.strip().lower()
        else:
            key = (
                f"{job.company or ''}-"
                f"{job.title or ''}"
            ).strip().lower()

        unique_jobs[key] = job

    jobs = list(unique_jobs.values())
    total_unique = len(jobs)

    jobs = filter_service.filter_recent(
        jobs,
        days=days_filter
    )

    total_recent = len(jobs)

    matches = []
    ignored_count = 0

    for job in jobs:
        relevance_result = relevance.evaluate(job)

        if not relevance_result["relevant"]:
            ignored_count += 1
            continue

        if not job.description or not job.description.strip():
            try:
                fetched_description = (
                    detail_service.get_description(job.url)
                )

                if fetched_description:
                    job.description = fetched_description

            except Exception:
                pass

        result = matcher.calculate(job)

        matches.append(
            {
                "job": job,
                "result": result,
                "relevance": relevance_result
            }
        )

        database.save(
            job,
            result.score
        )

    ranked_jobs = ranking.rank(matches)

    # Só exibe vagas com recomendação APLICAR ou AVALIAR.
    recommended_jobs = [
        item
        for item in ranked_jobs
        if item["result"].priority in {"ALTA", "MEDIA"}
    ]

    print("RESUMO")
    print("-" * 60)
    print(f"Vagas coletadas:       {total_collected}")
    print(f"Vagas únicas:          {total_unique}")
    print(f"Vagas recentes:        {total_recent}")
    print(f"Vagas fora do perfil:  {ignored_count}")
    print(f"Vagas recomendadas:    {len(recommended_jobs)}")
    print()

    print("=" * 60)
    print("🏆 MELHORES OPORTUNIDADES")
    print("=" * 60)

    if not recommended_jobs:
        print()
        print("Nenhuma oportunidade recomendada nesta execução.")

    for index, item in enumerate(
        recommended_jobs[:10],
        start=1
    ):
        job = item["job"]
        result = item["result"]

        print()
        print(f"{index}. {job.title}")
        print(f"   Empresa: {job.company}")
        print(f"   Localização: {job.location or 'Não informada'}")
        print(f"   Fonte: {job.source}")
        print(f"   Match: {result.score}%")
        print(f"   Ranking: {item['ranking_score']:.1f}")
        print(f"   Recomendação: {result.recommendation}")
        print(
            f"   Skills aderentes: "
            f"{', '.join(result.strengths) or 'Não identificadas'}"
        )
        print(f"   Link: {job.url}")

    print()
    print("=" * 60)
    print("✅ Execução finalizada")
    print("=" * 60)


if __name__ == "__main__":
    main()