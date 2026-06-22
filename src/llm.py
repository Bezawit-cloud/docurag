from groq import Groq
from src.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided context.
If the answer is not contained in the context, say "I don't have enough information in this document to answer that."
Do not make up information. Always be concise and direct."""

def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    question: str
    chunks: list of {id, content, similarity}
    """
    # Build the context string from the list of dictionaries
    context = "\n\n".join(
        f"[Source {i+1}]\n{chunk['content']}"
        for i, chunk in enumerate(chunks)
    )

    user_prompt = f"""Context from document:
{context}

Question: {question}

Answer the question using only the context above."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content