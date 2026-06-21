from langchain_groq import ChatGroq
from app.hf_embeddings import HFInferenceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.config import GROQ_API_KEY, LLM_MODEL, EMBED_MODEL, CHROMA_DIR, COLLECTION, TOP_K, HF_API_TOKEN

SYSTEM_PROMPT = """You are a helpful customer support assistant.
Use ONLY the context below to answer the question.
If the answer is not in the context, say:
"I don't have information on that. Please contact our support team."

Be concise and friendly.

Context:
{context}

Question: {question}
Answer:"""

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYSTEM_PROMPT,
)

def load_vectorstore():
    embeddings = HFInferenceEmbeddings(
        model=EMBED_MODEL,
        api_token=HF_API_TOKEN,
    )
    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    return vectorstore

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def build_rag_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=0.2,
        groq_api_key=GROQ_API_KEY,
    )
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | QA_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retriever

def format_sources(docs, answer: str = "") -> list[dict]:
    """
    Only return sources whose content meaningfully overlaps with
    the actual answer text. This avoids showing a file as a 'source'
    just because it was retrieved — it must have actually contributed
    words to the answer.
    """
    import re

    answer_words = set(re.findall(r"[a-z]{4,}", answer.lower()))

    seen = set()
    sources = []
    for doc in docs:
        src = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "")
        key = f"{src}-{page}"
        if key in seen:
            continue

        chunk_words = set(re.findall(r"[a-z]{4,}", doc.page_content.lower()))
        overlap = answer_words & chunk_words

        # Require a meaningful overlap (at least 3 shared significant words)
        if answer and len(overlap) < 3:
            continue

        seen.add(key)
        sources.append({
            "source": src,
            "page": page,
            "snippet": doc.page_content[:200].strip() + "...",
        })
    return sources