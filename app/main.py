from datetime import datetime, timezone, timedelta
from pathlib import Path
import re
import unicodedata

from app.agents.cv_optimizer import CVOptimizer
from app.agents.job_collector import JobCollectorAgent
from app.agents.match_agent import MatchAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.job_relevance_agent import JobRelevanceAgent

from app.config.candidate_profile import CANDIDATE_PROFILE
from app.database.database import JobDatabase

from app.services.job_detail_service import JobDetailService
from app.services.job_filter_service import JobFilterService


def build_search_terms():
    search_terms = []

    for tier in CANDIDATE_PROFILE["target_roles"].values():
        search_terms.extend(tier["roles"])

    return list(dict.fromkeys(search_terms))


def sanitize_filename(value):
    if not value:
        return "vaga"

    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = normalized.strip("_")

    return normalized or "vaga"


def display_job(index, item, include_details=True):
    job = item["job"]
    result = item["result"]

    print()
    print(f"{index}. {job.title}")
    print(f"   Empresa: {job.company}")
    print(f"   Localização: {job.location or 'Não informada'}")

    if include_details:
        print(f"   Fonte: {job.source}")
        print(f"   Match: {result.score}%")
        print(f"   Ranking: {item['ranking_score']:.1f}")
        print(f"   Recomendação: {result.recommendation}")
        print(
            "   Skills aderentes: "
            f"{', '.join(result.strengths) or 'Não identificadas'}"
        )
    else:
        print(f"   Match: {result.score}%")
        print(f"   Recomendação: {result.recommendation}")

    print(f"   Link: {job.url}")


def build_cv_content(job, optimization):
    matched_skills = optimization.get("matched_skills", [])
    ordered_skills = optimization.get("ordered_skills", [])

    skills_text = "\n".join(
        f"- {skill}"
        for skill in ordered_skills[:15]
    )

    matched_text = "\n".join(
        f"- {skill}"
        for skill in matched_skills[:10]
    )

    if not matched_text:
        matched_text = "- Nenhuma palavra-chave específica identificada."

    return f"""# Luciano Teixeira

## Objetivo

{job.title} — {job.company}

## Resumo profissional

{optimization["summary"]}

## Principais competências

{skills_text}

## Competências aderentes à vaga

{matched_text}

## Experiência em destaque

- Mais de 20 anos de experiência em tecnologia.
- Liderança de três squads multidisciplinares, com aproximadamente 20 profissionais.
- Gestão e desenvolvimento de pessoas, formação de lideranças técnicas e construção de equipes de alta performance.
- Atuação próxima a Produto e Negócio na definição de roadmap, discovery, priorização e evolução de produtos digitais.
- Experiência com CRM, e-commerce, canais digitais, atendimento omnichannel e mensageria.
- Implementação do canal de vendas via WhatsApp, com integrações de sistemas, meios de pagamento e inteligência artificial.
- Experiência com APIs, microsserviços, arquitetura de software, AWS, RabbitMQ, Kafka, SNS e SQS.
- Gestão por métricas como Lead Time, Cycle Time, Throughput, disponibilidade, SLA, SLO, MTTR e frequência de deploy.

## Vaga

- Empresa: {job.company}
- Cargo: {job.title}
- Localização: {job.location or "Não informada"}
- Link: {job.url}
"""


def build_linkedin_message(job, optimization):
    matched_skills = optimization.get("matched_skills", [])

    skills = ", ".join(matched_skills[:4])

    skills_sentence = ""

    if skills:
        skills_sentence = (
            f" Tenho experiência aderente em {skills}."
        )

    return (
        f"Olá, tudo bem?\n\n"
        f"Vi a oportunidade para {job.title} na {job.company} "
        f"e acredito que meu perfil possui boa aderência à posição."
        f"{skills_sentence}\n\n"
        f"Tenho mais de 20 anos de experiência em tecnologia e, "
        f"na minha última atuação na Petz, liderei três squads "
        f"multidisciplinares responsáveis por produtos digitais, "
        f"CRM, e-commerce, canais omnichannel, integrações, "
        f"mensageria e iniciativas com inteligência artificial.\n\n"
        f"Gostaria de me colocar à disposição para conversar sobre "
        f"a oportunidade.\n\n"
        f"LinkedIn: "
        f"https://www.linkedin.com/in/luciano-teixeira-7b44b325\n\n"
        f"Obrigado,\n"
        f"Luciano Teixeira\n"
    )


def build_cover_letter(job, optimization):
    matched_skills = optimization.get("matched_skills", [])

    skills = ", ".join(matched_skills[:6])

    if not skills:
        skills = (
            "liderança de engenharia, gestão de pessoas, "
            "arquitetura de software e produtos digitais"
        )

    return (
        f"Olá,\n\n"
        f"Tenho interesse na oportunidade de {job.title} "
        f"na {job.company}.\n\n"
        f"Sou líder de tecnologia com mais de 20 anos de experiência, "
        f"atuando na conexão entre Engenharia, Produto e Negócio. "
        f"Minha trajetória inclui liderança de equipes multidisciplinares, "
        f"desenvolvimento de pessoas, transformação digital e evolução "
        f"de plataformas e produtos críticos.\n\n"
        f"Na Petz, liderei três squads, com aproximadamente 20 profissionais, "
        f"responsáveis por CRM, e-commerce, atendimento omnichannel, "
        f"mensageria, integrações e pelo canal de vendas via WhatsApp. "
        f"Também participei de iniciativas envolvendo inteligência artificial, "
        f"bots integrados ao Zendesk e meios de pagamento.\n\n"
        f"Para esta posição, destaco minha experiência em {skills}. "
        f"Tenho facilidade para trabalhar com diferentes áreas, transformar "
        f"necessidades de negócio em soluções tecnológicas e apoiar os times "
        f"na entrega de resultados com qualidade e previsibilidade.\n\n"
        f"Fico à disposição para conversar sobre como minha experiência "
        f"pode contribuir com os desafios da {job.company}.\n\n"
        f"Atenciosamente,\n"
        f"Luciano Teixeira\n"
        f"LinkedIn: "
        f"https://www.linkedin.com/in/luciano-teixeira-7b44b325\n"
    )


def generate_application_files(item):
    job = item["job"]

    optimizer = CVOptimizer()
    optimization = optimizer.optimize(job)

    company_name = sanitize_filename(job.company)
    job_title = sanitize_filename(job.title)

    output_directory = Path("output") / f"{company_name}_{job_title}"
    output_directory.mkdir(parents=True, exist_ok=True)

    cv_path = output_directory / "cv_adaptado.md"
    linkedin_path = output_directory / "mensagem_linkedin.txt"
    cover_letter_path = output_directory / "carta_apresentacao.txt"
    job_path = output_directory / "vaga.txt"

    cv_path.write_text(
        build_cv_content(job, optimization),
        encoding="utf-8"
    )

    linkedin_path.write_text(
        build_linkedin_message(job, optimization),
        encoding="utf-8"
    )

    cover_letter_path.write_text(
        build_cover_letter(job, optimization),
        encoding="utf-8"
    )

    job_path.write_text(
        (
            f"Empresa: {job.company}\n"
            f"Cargo: {job.title}\n"
            f"Localização: {job.location or 'Não informada'}\n"
            f"Fonte: {job.source}\n"
            f"Link: {job.url}\n\n"
            f"Descrição:\n{job.description or 'Não disponível'}\n"
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("✅ MATERIAIS GERADOS")
    print("=" * 60)
    print(f"Empresa: {job.company}")
    print(f"Cargo: {job.title}")
    print()
    print(f"CV adaptado:         {cv_path}")
    print(f"Mensagem LinkedIn:   {linkedin_path}")
    print(f"Carta apresentação:  {cover_letter_path}")
    print(f"Dados da vaga:       {job_path}")


def select_job(available_jobs):
    if not available_jobs:
        return

    print()
    print("=" * 60)
    print("GERAR MATERIAL PARA CANDIDATURA")
    print("=" * 60)
    print("Digite o número da vaga ou 0 para encerrar.")

    while True:
        choice = input("\nEscolha: ").strip()

        if choice == "0":
            return

        if not choice.isdigit():
            print("Digite apenas o número da vaga.")
            continue

        selected_index = int(choice)

        if selected_index < 1 or selected_index > len(available_jobs):
            print(
                f"Escolha um número entre 1 e "
                f"{len(available_jobs)}."
            )
            continue

        selected_item = available_jobs[selected_index - 1]
        generate_application_files(selected_item)
        return


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

    search_config = CANDIDATE_PROFILE["search"]
    days_filter = search_config["days"]
    maximum_results = search_config["maximum_results"]
    minimum_match_score = search_config["minimum_match_score"]

    jobs = []

    print("=" * 60)
    print("🚀 JOBHUNTER AI")
    print("=" * 60)
    print(f"Candidato: {CANDIDATE_PROFILE['name']}")
    print(f"Execução: {current_time.strftime('%d/%m/%Y %H:%M')}")
    print(f"Período analisado: últimos {days_filter} dias")
    print()

    for term in search_terms:
        try:
            jobs.extend(collector.search(term))
        except Exception as error:
            print(f"Erro ao pesquisar '{term}': {error}")

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
                fetched_description = detail_service.get_description(
                    job.url
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
                "relevance": relevance_result,
            }
        )

        database.save(
            job,
            result.score
        )

    ranked_jobs = ranking.rank(matches)

    priority_jobs = [
        item
        for item in ranked_jobs
        if item["relevance"]["score"] >= 90
        and item["result"].score >= minimum_match_score
    ]

    fallback_jobs = [
        item
        for item in ranked_jobs
        if 70 <= item["relevance"]["score"] < 90
        and item["result"].score >= minimum_match_score
    ]

    selected_priority_jobs = priority_jobs[:maximum_results]
    selected_fallback_jobs = fallback_jobs[:3]

    print("RESUMO")
    print("-" * 60)
    print(f"Vagas coletadas:       {total_collected}")
    print(f"Vagas únicas:          {total_unique}")
    print(f"Vagas recentes:        {total_recent}")
    print(f"Vagas fora do perfil:  {ignored_count}")
    print(f"Vagas prioritárias:    {len(priority_jobs)}")
    print(f"Vagas alternativas:    {len(fallback_jobs)}")
    print()

    available_jobs = []
    display_index = 1

    print("=" * 60)
    print("🏆 OPORTUNIDADES PRIORITÁRIAS")
    print("=" * 60)

    if not selected_priority_jobs:
        print()
        print("Nenhuma oportunidade prioritária nesta execução.")

    for item in selected_priority_jobs:
        display_job(display_index, item, include_details=True)
        available_jobs.append(item)
        display_index += 1

    print()
    print("=" * 60)
    print("🟡 OPORTUNIDADES ALTERNATIVAS")
    print("=" * 60)

    if not selected_fallback_jobs:
        print()
        print("Nenhuma oportunidade alternativa nesta execução.")

    for item in selected_fallback_jobs:
        display_job(display_index, item, include_details=False)
        available_jobs.append(item)
        display_index += 1

    select_job(available_jobs)

    print()
    print("=" * 60)
    print("✅ Execução finalizada")
    print("=" * 60)


if __name__ == "__main__":
    main()