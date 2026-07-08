from datetime import datetime, timezone, timedelta

from app.agents.job_collector import JobCollectorAgent
from app.agents.match_agent import MatchAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.job_relevance_agent import JobRelevanceAgent

from app.database.database import JobDatabase

from app.services.job_detail_service import JobDetailService
from app.services.job_filter_service import JobFilterService


def main():

    brasil_timezone = timezone(timedelta(hours=-3))

    current_time = datetime.now(brasil_timezone)

    print("=" * 50)
    print("🚀 JobHunter AI iniciado")
    print("=" * 50)
    print(
        f"Data: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print()


    collector = JobCollectorAgent()
    matcher = MatchAgent()
    ranking = RankingAgent()
    relevance = JobRelevanceAgent()

    database = JobDatabase()

    detail_service = JobDetailService()
    filter_service = JobFilterService()


    search_terms = [

        "Engineering Manager",
        "Tech Manager",
        "Technical Product Manager Senior",
        "Software Engineering Manager",
        "Engineering Lead",
        "Gerente de Engenharia",
        "Gerente de Tecnologia"

    ]


    jobs = []


    print("🔎 Iniciando busca de vagas")
    print()


    for term in search_terms:

        print(
            f"🔎 Buscando vagas para: {term}"
        )

        results = collector.search(term)

        print(
            f"   Encontradas: {len(results)}"
        )

        jobs.extend(results)



    print()
    print(
        f"Total bruto encontrado: {len(jobs)}"
    )


    # Remove duplicidades

    unique_jobs = {}


    for job in jobs:

        key = (
            f"{job.company}-"
            f"{job.title}-"
            f"{job.url}"
        )


        unique_jobs[key] = job



    jobs = list(unique_jobs.values())


    print(
        f"Após remover duplicadas: {len(jobs)}"
    )


    # Filtro últimos 7 dias

    jobs = filter_service.filter_recent(
        jobs,
        days=7
    )


    print(
        f"Após filtro 7 dias: {len(jobs)}"
    )


    matches = []

    relevant_count = 0
    ignored_count = 0


    for job in jobs:


        relevance_result = relevance.evaluate(job)


        if not relevance_result["relevant"]:

            ignored_count += 1

            print(
                f"❌ Ignorada: {job.title}"
            )

            continue



        relevant_count += 1


        job.description = detail_service.get_description(
            job.url
        )


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



    print()
    print(
        f"✅ Vagas relevantes: {relevant_count}"
    )

    print(
        f"❌ Vagas ignoradas: {ignored_count}"
    )



    ranked_jobs = ranking.rank(
        matches
    )



    print()
    print("=" * 50)
    print("🏆 TOP 10 VAGAS PARA LUCIANO")
    print("=" * 50)



    for item in ranked_jobs[:10]:


        job = item["job"]
        result = item["result"]
        relevance_result = item["relevance"]


        print()
        print("-----------------------")
        print(
            f"Empresa: {job.company}"
        )

        print(
            f"Cargo: {job.title}"
        )

        print(
            f"Link: {job.url}"
        )

        print(
            f"Fonte: {job.source}"
        )

        print(
            f"Localização: {job.location}"
        )

        print(
            f"Publicado: {job.published_at}"
        )

        print(
            f"Prioridade cargo: {relevance_result['score']}"
        )

        print(
            f"Ranking final: {item['ranking_score']:.1f}"
        )

        print(
            f"Categoria: {relevance_result['category']}"
        )

        print(
            f"Match: {result.score}%"
        )

        print(
            f"Skills: {result.strengths}"
        )

        print(
            f"Recomendação: {result.recommendation}"
        )

        print(
            f"Prioridade: {result.priority}"
        )


    print()
    print("✅ Vagas salvas no banco")



if __name__ == "__main__":
    main()