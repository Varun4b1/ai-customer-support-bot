from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, LLM_MODEL

SYSTEM_PROMPT = """You are a helpful, honest assistant.

Important rules:
- If you are not confident about a fact, say so explicitly rather than guessing.
- Never state speculation or guesses as if they were verified facts.
- For specific numbers, dates, names, or claims you are not certain about, say
  "I'm not fully certain, but..." or "I don't have reliable information on that."
- Prefer saying "I don't know" over inventing a plausible-sounding answer.
- Keep answers concise and direct.
"""


def build_rag_chain():
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=0.2,
        groq_api_key=GROQ_API_KEY,
    )

    class SimpleChain:
        def invoke(self, question: str) -> str:
            messages = [
                ("system", SYSTEM_PROMPT),
                ("human", question),
            ]
            response = llm.invoke(messages)
            return response.content

    # retriever kept as None — main.py checks for this and skips source lookup
    return SimpleChain(), None


def format_sources(docs, answer: str = ""):
    return []