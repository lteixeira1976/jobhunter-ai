from dataclasses import dataclass
from typing import List


@dataclass
class ProfessionalProfile:

    name: str
    skills: List[str]
    roles: List[str]


luciano_profile = ProfessionalProfile(
    name="Luciano Teixeira",

    skills=[
        # Liderança e Gestão
        "Gestão de Times de Tecnologia",
        "Liderança Técnica",
        "Engineering Management",
        "People Management",
        "Gestão Humanizada",
        "Mentoria",
        "Desenvolvimento de Lideranças",
        "Gestão de Stakeholders",

        # Produto e Estratégia
        "Technical Product Manager",
        "Product Management",
        "Gestão de Produtos Digitais",
        "Roadmap",
        "Priorização de Backlog",
        "Discovery",
        "Métricas de Produto",
        "Métricas de Engenharia",
        "Data Driven Decision",

        # Engenharia de Software
        "Engenharia de Software",
        "Arquitetura de Software",
        "Arquitetura de Soluções",
        "APIs REST",
        "Microsserviços",
        "Integrações de Sistemas",
        "Integração com Gateways de Pagamento",
        "Sistemas Distribuídos",

        # Linguagens e Frameworks
        "Java",
        "Spring Boot",
        "Python",
        "SQL",
        "JavaScript",

        # Cloud e DevOps
        "Cloud Computing",
        "AWS",
        "Azure",
        "CI/CD",
        "DevOps",
        "DevSecOps",
        "Automação de Deploy",

        # Mensageria e Integrações
        "RabbitMQ",
        "Mensageria",
        "Kafka",
        "Eventos",
        "Integrações B2B",

        # Métodos e Processos
        "Agile",
        "Scrum",
        "Kanban",
        "Team Topologies",
        "Gestão de Dívida Técnica",

        # Qualidade e Segurança
        "Qualidade de Software",
        "Testes Automatizados",
        "Observabilidade",
        "SLA",
        "SLO",
        "MTTR",
        "Segurança de Aplicações",
        "OWASP"

    ],

    roles=[
        "Engineering Manager",
        "Technical Product Manager",
        "Tech Manager",
        "Gerente de engenharia de software"
    
)