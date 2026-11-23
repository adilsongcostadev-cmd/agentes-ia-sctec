# 🤖 Agentes de IA — SCTEC

Exercícios resolvidos do curso **Agentes de IA (T1)** do Programa SCTEC — Carreira Tech.

O repositório reúne agentes construídos com **LangGraph**, **LangChain** e modelos hospedados na **Groq**, aplicando o ciclo **ReAct** (percepção → raciocínio → ação → observação), ferramentas estruturadas com **Pydantic** e boas práticas de engenharia de prompt.

---

## 📚 Índice

| Semana | Tema | Exercício | Status |
|---|---|---|---|
| [01](./semana01) | Fundamentos e desenho de agentes | Assistente Virtual da Biblioteca Tech | ✅ Concluído |

---

## 🛠️ Stack

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Ambiente e dependências | [uv](https://docs.astral.sh/uv/) |
| Orquestração de agentes | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| Integração com LLMs | [LangChain](https://python.langchain.com/) + `langchain-groq` |
| Inferência | [Groq](https://console.groq.com/) — `openai/gpt-oss-120b` |
| Validação de dados | [Pydantic](https://docs.pydantic.dev/) |
| Segredos | `python-dotenv` (`.env` fora do versionamento) |

---

## 🚀 Como executar

Pré-requisitos: [Git](https://git-scm.com/), [uv](https://docs.astral.sh/uv/) e uma chave de API da [Groq](https://console.groq.com/keys).

```bash
# 1. Clonar o repositório
git clone https://github.com/adilsongcostadev-cmd/agentes-ia-sctec.git
cd agentes-ia-sctec/semana01

# 2. Criar o arquivo .env com a chave da Groq
echo "GROQ_API_KEY=sua_chave_aqui" > .env

# 3. Recriar o ambiente a partir do uv.lock
uv sync

# 4. Executar o agente
uv run biblioteca.py
```

---

## 🗂️ Estrutura

```
agentes-ia-sctec/
├── README.md              ← este arquivo
└── semana01/
    ├── README.md          ← detalhes do exercício e resultados dos testes
    ├── biblioteca.py      ← agente Biblioteca Tech (LangGraph + 2 ferramentas)
    ├── main.py            ← teste de conexão com a Groq
    ├── pyproject.toml     ← dependências do projeto
    └── uv.lock            ← versões exatas (reprodutibilidade)
```

Cada semana é um projeto `uv` independente, com seu próprio ambiente virtual.

---

## ⚠️ Nota sobre modelos

Os materiais do curso citam `llama-3.3-70b-versatile` e `llama-3.1-8b-instant`, **desativados pela Groq em 16/08/2026**. Este repositório adota os substitutos oficiais recomendados na [página de descontinuações da Groq](https://console.groq.com/docs/deprecations): `openai/gpt-oss-120b` e `openai/gpt-oss-20b`.

---

## 👤 Autor

**Adilson Guimarães Costa**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-adilsongcosta-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adilsongcosta)
[![GitHub](https://img.shields.io/badge/GitHub-adilsongcostadev--cmd-181717?logo=github&logoColor=white)](https://github.com/adilsongcostadev-cmd)