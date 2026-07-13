import os
import csv
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

SEARCH_TERMS = [
    "Engineering Manager São Paulo",
    "Gerente de Engenharia de Software São Paulo",
    "Tech Manager São Paulo",
    "Gerente de Tecnologia São Paulo",
    "Technical Product Manager São Paulo",
    "Software Engineering Manager Brazil remote",
]

POSITIVE_TERMS = [
    "engineering manager",
    "gerente de engenharia",
    "tech manager",
    "gerente de tecnologia",
    "technical product manager",
    "software engineering manager",
    "liderança",
    "gestão de pessoas",
    "produto",
    "api",
    "apis",
    "microservices",
    "microsserviços",
    "java",
    "python",
    "spring",
    "aws",
    "kafka",
    "rabbitmq",
    "sqs",
    "sns",
    "zendesk",
    "whatsapp",
]

NEGATIVE_TERMS = [
    "estágio",
    "trainee",
    "júnior",
    "junior",
    "intern",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 JobHunterAI-POC"
}


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def serpapi_google_jobs(query):
    if not SERPAPI_KEY:
        raise RuntimeError("Defina SERPAPI_KEY no ambiente.")

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "pt-br",
        "gl": "br",
        "api_key": SERPAPI_KEY,
    }

    r = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    jobs = []

    for item in data.get("jobs_results", []):
        apply_link = ""

        apply_options = item.get("apply_options") or []
        if apply_options:
            apply_link = apply_options[0].get("link", "")

        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", ""),
            "location": item.get("location", ""),
            "source": "SerpAPI Google Jobs",
            "url": apply_link,
            "description": item.get("description", ""),
            "detected_extensions": json.dumps(item.get("detected_extensions", {}), ensure_ascii=False),
            "query": query,
        })

    return jobs


def extract_from_json_ld(soup):
    descriptions = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        items = data if isinstance(data, list) else [data]

        for item in items:
            if not isinstance(item, dict):
                continue

            if item.get("@type") == "JobPosting":
                desc = item.get("description", "")
                title = item.get("title", "")
                company = ""

                hiring_org = item.get("hiringOrganization")
                if isinstance(hiring_org, dict):
                    company = hiring_org.get("name", "")

                location = ""
                job_location = item.get("jobLocation")
                if isinstance(job_location, dict):
                    address = job_location.get("address", {})
                    if isinstance(address, dict):
                        location = " ".join([
                            str(address.get("addressLocality", "")),
                            str(address.get("addressRegion", "")),
                            str(address.get("addressCountry", "")),
                        ])

                descriptions.append({
                    "title": clean_text(title),
                    "company": clean_text(company),
                    "location": clean_text(location),
                    "description": clean_text(BeautifulSoup(desc, "html.parser").get_text(" ")),
                })

    return descriptions[0] if descriptions else {}


def fetch_job_page(url):
    if not url:
        return {}

    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        return {}

    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code >= 400:
            return {"fetch_status": r.status_code}
    except Exception as e:
        return {"fetch_error": str(e)}

    soup = BeautifulSoup(r.text, "html.parser")

    json_ld = extract_from_json_ld(soup)

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_desc = meta.get("content", "")

    page_text = clean_text(soup.get_text(" "))
    page_text = page_text[:12000]

    return {
        "fetch_status": r.status_code,
        "final_url": r.url,
        "jsonld_title": json_ld.get("title", ""),
        "jsonld_company": json_ld.get("company", ""),
        "jsonld_location": json_ld.get("location", ""),
        "jsonld_description": json_ld.get("description", ""),
        "meta_description": clean_text(meta_desc),
        "page_text": page_text,
    }


def score_job(job):
    text = " ".join([
        job.get("title", ""),
        job.get("company", ""),
        job.get("location", ""),
        job.get("description", ""),
        job.get("jsonld_description", ""),
        job.get("meta_description", ""),
        job.get("page_text", ""),
    ]).lower()

    positives = [term for term in POSITIVE_TERMS if term in text]
    negatives = [term for term in NEGATIVE_TERMS if term in text]

    score = min(100, len(positives) * 8)
    score -= len(negatives) * 25
    score = max(0, score)

    if score >= 60:
        priority = "ALTA"
    elif score >= 35:
        priority = "MEDIA"
    else:
        priority = "BAIXA"

    return score, priority, positives, negatives


def main():
    all_jobs = {}

    for query in SEARCH_TERMS:
        print(f"Buscando: {query}")
        jobs = serpapi_google_jobs(query)

        for job in jobs:
            key = job.get("url") or f"{job.get('title')}|{job.get('company')}|{job.get('location')}"
            all_jobs[key] = job

        time.sleep(1)

    print(f"Vagas únicas encontradas: {len(all_jobs)}")

    enriched = []

    for idx, job in enumerate(all_jobs.values(), start=1):
        print(f"[{idx}/{len(all_jobs)}] Enriquecendo: {job.get('title')} - {job.get('company')}")

        page_data = fetch_job_page(job.get("url", ""))
        job.update(page_data)

        if not job.get("description") and job.get("jsonld_description"):
            job["description"] = job["jsonld_description"]

        score, priority, positives, negatives = score_job(job)

        job["score"] = score
        job["priority"] = priority
        job["positive_matches"] = ", ".join(positives)
        job["negative_matches"] = ", ".join(negatives)

        enriched.append(job)
        time.sleep(1)

    enriched.sort(key=lambda x: x["score"], reverse=True)

    with open("poc_google_jobs_result.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "score",
            "priority",
            "title",
            "company",
            "location",
            "url",
            "positive_matches",
            "negative_matches",
            "description",
            "jsonld_description",
            "meta_description",
            "fetch_status",
            "final_url",
            "query",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(enriched)

    print("\nTOP oportunidades:")
    for job in enriched[:10]:
        print("-" * 60)
        print(f"{job['score']}% | {job['priority']} | {job.get('title')} | {job.get('company')}")
        print(job.get("url"))

    print("\nArquivo gerado: poc_google_jobs_result.csv")


if __name__ == "__main__":
    main()