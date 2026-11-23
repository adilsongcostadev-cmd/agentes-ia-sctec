# Semana 1 — Agentes de IA (SCTEC)

Exercícios da Semana 1 do curso **Agentes de IA (T1)** — Programa SCTEC.

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `main.py` | Teste de conexão do ambiente com a API da Groq |
| `biblioteca.py` | Exercício **Assistente Virtual da Biblioteca Tech** (LangGraph + ferramentas) |

## Ambiente

- Gerenciador: [uv](https://docs.astral.sh/uv/)
- Python 3.12
- Dependências: `groq`, `langgraph`, `langchain-groq`, `pydantic`, `python-dotenv`

```bash
uv sync                  # recria o ambiente a partir do uv.lock
uv run biblioteca.py     # executa os casos de teste
```

Crie um arquivo `.env` na pasta com a sua chave (não versionado):

```
GROQ_API_KEY=sua_chave_api_groq_aqui
```

## Observação sobre o modelo utilizado

O enunciado indica os modelos `llama-3.3-70b-versatile` e `llama-3.1-8b-instant`.
**Ambos foram desativados pela Groq em 16/08/2026.** Conforme a página oficial de
descontinuações da Groq (https://console.groq.com/docs/deprecations), os substitutos
recomendados são:

| Modelo do enunciado | Substituto adotado |
|---|---|
| `llama-3.3-70b-versatile` | `openai/gpt-oss-120b` |
| `llama-3.1-8b-instant` | `openai/gpt-oss-20b` |

Este projeto utiliza **`openai/gpt-oss-120b`** com `temperature=0`.

## Exercício: Biblioteca Tech

### Arquitetura

```
START → agente ──(tool_call?)──► ferramentas
          ▲                          │
          └──────────────────────────┘
          │
          └──(sem tool_call)──► END
```

- **Estado:** `EstadoAgente` com a lista de mensagens (`add_messages`)
- **Nó `agente`:** LLM com `bind_tools`
- **Nó `ferramentas`:** `ToolNode`
- **Aresta condicional:** `tools_condition`

### Ferramentas

- `consultar_acervo(titulo)` — entrada validada por Pydantic; retorna `titulo`,
  `disponivel`, `localizacao` e o campo adicional `encontrado`, que distingue
  "livro inexistente" de "livro emprestado" e evita alucinação.
- `listar_horario_funcionamento()` *(bônus)* — retorna o dia da semana, a data,
  se hoje é feriado nacional e o horário do dia, pois o LLM não tem acesso ao
  relógio do sistema.

### Horário de funcionamento (fictício)

- Segunda a sexta: 09:00 às 22:00
- Sábado: 08:00 às 12:00
- Domingo e feriados nacionais: fechada

### Resultados dos casos de teste

| Caso | Pergunta | Ferramenta chamada | Resultado |
|---|---|---|---|
| 1. Esperado | "Olá, vocês têm o livro Clean Code disponível?" | `consultar_acervo` | ✅ Disponível — Corredor A - Prateleira 2 |
| 2. Ambiguidade | "Quero pegar um livro emprestado hoje, tem vaga?" | nenhuma | ✅ Pede o título da obra |
| 3. Não encontrado | "Vocês têm o livro Harry Potter e a Pedra Filosofal?" | `consultar_acervo` | ✅ Não consta no acervo, sem alucinação |
| 4. Bônus | "Que horas a biblioteca fecha hoje?" | `listar_horario_funcionamento` | ✅ Fecha às 22:00 (segunda-feira) |