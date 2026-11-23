import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Carrega as variáveis definidas no arquivo .env
load_dotenv()


def main():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("A variável GROQ_API_KEY não foi encontrada no arquivo .env.")

    llm = ChatGroq(
        model="openai/gpt-oss-120b",  # substitui o llama-3.3-70b-versatile (desativado em 16/08/2026)
        temperature=0.2,
    )

    resposta = llm.invoke("Olá! Confirme em uma frase que o ambiente está funcionando.")
    print("Resposta do agente:", resposta.content)


if __name__ == "__main__":
    main()