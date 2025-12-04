from groq import Groq
from config import GROQ_API_KEY

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def ask_groq(system_prompt, user_prompt):
    if not groq_client:
        return None

    res = groq_client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=500
    )
    return res.choices[0].message.content
