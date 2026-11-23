from datetime import date, datetime
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ---------------------------------------------------------------
# 1. Dados fictícios: acervo, horários e feriados
# ---------------------------------------------------------------
ACERVO = {
    "clean code": {
        "titulo": "Clean Code",
        "disponivel": True,
        "localizacao": "Corredor A - Prateleira 2",
    },
    "inteligência artificial: uma abordagem moderna": {
        "titulo": "Inteligência Artificial: Uma Abordagem Moderna",
        "disponivel": False,
        "localizacao": "Emprestado (Devolução em 3 dias)",
    },
    "estruturas de dados e algoritmos com python": {
        "titulo": "Estruturas de Dados e Algoritmos com Python",
        "disponivel": True,
        "localizacao": "Corredor C - Prateleira 1",
    },
}

DIAS_SEMANA = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]

HORARIOS = {
    "segunda-feira": "09:00 às 22:00",
    "terça-feira": "09:00 às 22:00",
    "quarta-feira": "09:00 às 22:00",
    "quinta-feira": "09:00 às 22:00",
    "sexta-feira": "09:00 às 22:00",
    "sábado": "08:00 às 12:00",
    "domingo": "Fechada",
    "feriado": "Fechada",
}

# Feriados nacionais de data fixa: (mês, dia) -> nome
FERIADOS_FIXOS = {
    (1, 1): "Confraternização Universal",
    (4, 21): "Tiradentes",
    (5, 1): "Dia do Trabalho",
    (9, 7): "Independência do Brasil",
    (10, 12): "Nossa Senhora Aparecida",
    (11, 2): "Finados",
    (11, 15): "Proclamação da República",
    (11, 20): "Dia Nacional de Zumbi e da Consciência Negra",
    (12, 25): "Natal",
}

# Feriados nacionais de data móvel (dependem da Páscoa)
FERIADOS_MOVEIS = {
    date(2026, 4, 3): "Sexta-feira Santa",
    date(2027, 3, 26): "Sexta-feira Santa",
}


def feriado_do_dia(dia: date) -> str | None:
    """Retorna o nome do feriado nacional na data informada, ou None."""
    return FERIADOS_MOVEIS.get(dia) or FERIADOS_FIXOS.get((dia.month, dia.day))


# ---------------------------------------------------------------
# 2. Ferramentas
# ---------------------------------------------------------------
class ConsultaAcervoInput(BaseModel):
    titulo: str = Field(
        description="Título exato do livro informado pelo aluno. Ex.: 'Clean Code'."
    )


@tool("consultar_acervo", args_schema=ConsultaAcervoInput)
def consultar_acervo(titulo: str) -> dict:
    """Consulta o acervo da Biblioteca Tech e informa se um livro
    está disponível para empréstimo e onde encontrá-lo."""
    registro = ACERVO.get(titulo.strip().lower())
    if registro is None:
        return {
            "titulo": titulo,
            "encontrado": False,
            "disponivel": False,
            "localizacao": None,
        }
    return {**registro, "encontrado": True}


@tool("listar_horario_funcionamento")
def listar_horario_funcionamento() -> dict:
    """Retorna o horário de funcionamento da Biblioteca Tech: o dia e a data
    de hoje, se hoje é feriado, o horário de hoje e o quadro semanal."""
    agora = datetime.now()
    dia_semana = DIAS_SEMANA[agora.weekday()]
    feriado = feriado_do_dia(agora.date())

    if feriado:
        horario_hoje = f"{HORARIOS['feriado']} (feriado: {feriado})"
    else:
        horario_hoje = HORARIOS[dia_semana]

    return {
        "hoje": dia_semana,
        "data": agora.strftime("%d/%m/%Y"),
        "feriado": feriado,
        "horario_hoje": horario_hoje,
        "horarios_semana": HORARIOS,
    }


# ---------------------------------------------------------------
# 3. Prompt de sistema
# ---------------------------------------------------------------
SYSTEM_PROMPT = """Você é o bibliotecário virtual da Biblioteca Tech: prestativo, cordial e objetivo.

OBJETIVO
Informar aos alunos a disponibilidade e a localização dos livros do acervo
e o horário de funcionamento da biblioteca.

REGRAS
1. Para livros, use exclusivamente a ferramenta consultar_acervo.
2. Para horários, use exclusivamente a ferramenta listar_horario_funcionamento.
   Nunca presuma o dia da semana nem se é feriado: essas informações vêm da ferramenta.
3. Nunca invente livros, disponibilidades, prateleiras, prazos ou horários.
4. Se o aluno pedir um livro sem informar o título, NÃO chame a ferramenta: peça o nome da obra.
5. Se consultar_acervo retornar encontrado = false, informe educadamente que o livro não consta no acervo.
6. Responda apenas sobre o acervo e o funcionamento da biblioteca; recuse com cortesia outros assuntos.

FORMATO DE SAÍDA
Ao informar sobre um livro, responda sempre em tópicos curtos:
- **Livro:** <título>
- **Situação:** <Disponível | Emprestado | Não consta no acervo>
- **Onde encontrar:** <localização ou "—">
Ao informar horários, responda em uma ou duas frases curtas.
"""


# ---------------------------------------------------------------
# 4. Estado e nós do grafo
# ---------------------------------------------------------------
class EstadoAgente(TypedDict):
    # add_messages = "reducer": cada nó ANEXA mensagens à lista, em vez de substituí-la
    messages: Annotated[list, add_messages]


FERRAMENTAS = [consultar_acervo, listar_horario_funcionamento]

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
llm_com_ferramentas = llm.bind_tools(FERRAMENTAS)


def agente(estado: EstadoAgente):
    """Nó de raciocínio: o LLM lê o histórico e decide responder ou chamar ferramenta."""
    mensagens = [SystemMessage(content=SYSTEM_PROMPT)] + estado["messages"]
    resposta = llm_com_ferramentas.invoke(mensagens)
    return {"messages": [resposta]}


# ---------------------------------------------------------------
# 5. Montagem do grafo
# ---------------------------------------------------------------
grafo = StateGraph(EstadoAgente)

grafo.add_node("agente", agente)
grafo.add_node("ferramentas", ToolNode(FERRAMENTAS))

grafo.add_edge(START, "agente")
grafo.add_conditional_edges(
    "agente",
    tools_condition,
    {"tools": "ferramentas", END: END},
)
grafo.add_edge("ferramentas", "agente")

app = grafo.compile()


# ---------------------------------------------------------------
# 6. Casos de teste (3 obrigatórios + bônus)
# ---------------------------------------------------------------
CASOS_DE_TESTE = [
    ("1. Caso esperado", "Olá, vocês têm o livro Clean Code disponível?"),
    ("2. Caso de ambiguidade", "Quero pegar um livro emprestado hoje, tem vaga?"),
    ("3. Caso de falha / não encontrado", "Vocês têm o livro Harry Potter e a Pedra Filosofal?"),
    ("4. Bônus: horário", "Que horas a biblioteca fecha hoje?"),
]


def executar(pergunta: str) -> None:
    resultado = app.invoke({"messages": [HumanMessage(content=pergunta)]})
    mensagens = resultado["messages"]

    chamadas = [
        f'{tc["name"]}({tc["args"]})'
        for msg in mensagens
        for tc in getattr(msg, "tool_calls", []) or []
    ]

    print(f"ALUNO      : {pergunta}")
    print(f"FERRAMENTA : {', '.join(chamadas) if chamadas else 'nenhuma chamada'}")
    print(f"AGENTE     :\n{mensagens[-1].content}")


if __name__ == "__main__":
    for nome, pergunta in CASOS_DE_TESTE:
        print("\n" + "=" * 70)
        print(nome)
        print("=" * 70)
        executar(pergunta)