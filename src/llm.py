# src/llm.py
from groq import Groq
from src.config import settings

client = Groq(api_key=settings.groq_api_key)

def generate_answer(context: str, question: str) -> str:
    prompt = f"""You are a precise document assistant.
    Answer ONLY using the context below.
    If the answer is not in the context, say "I cannot find this in the document."
    
    Context:
    {context}
    
    Question: {question}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content