from groq import Groq
from src.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert document analysis assistant. 
Your task is to provide thorough, structured, and accurate explanations based STRICTLY on the provided context.

Follow these rules:
1. Deconstruct the concept: Provide a clear summary followed by a bulleted list of key components, characteristics, or steps found in the text.
2. Incorporate evidence: If the document provides examples, numeric data, or specific terminology, you MUST include them to support your explanation.
3. Be comprehensive: Aim for 3–5 sentences of explanation plus a structured breakdown. Do not provide one-sentence answers.
4. Strict Scope: If the answer is not in the context, say "I don't have enough information in this document to answer that." 
5. Do not hallucinate or add outside knowledge."""

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