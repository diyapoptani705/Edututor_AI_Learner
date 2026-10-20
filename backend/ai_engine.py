import os, json, re

try:
    from groq import Groq
except Exception:
    Groq = None

MODEL = os.getenv('EDUTUTOR_MODEL', 'llama-3.3-70b-versatile')
SYSTEM = '''You are EduTutor AI, a friendly, patient academic tutor. Explain step-by-step in simple language, use examples, and finish with a short takeaway. Stay focused on education. Do not claim to be a human.'''


def _client():
    key = os.getenv('GROQ_API_KEY')
    if not key or Groq is None:
        return None
    return Groq(api_key=key)


def ask_llm(messages, system=SYSTEM, max_tokens=1200):
    client = _client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'system', 'content': system}] + messages,
            temperature=0.4,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception:
        # Keep the demo usable if the key is missing, invalid, rate-limited, or offline.
        return None


def tutor(question, subject, grade, history=None):
    msgs = list(history or [])[-8:]
    msgs.append({'role': 'user', 'content': f'Subject: {subject}\nLevel: {grade}\nQuestion: {question}'})
    result = ask_llm(msgs)
    if result:
        return result
    return f'''### {subject} — Guided Explanation\n\n**Question:** {question}\n\nEduTutor is currently in **Demo Mode**. The app can still demonstrate the complete learning workflow without exposing or storing an API key in the frontend.\n\n**How to approach it**\n1. Identify the main concept involved.\n2. Break the problem into smaller steps.\n3. Apply the relevant rule, formula, or definition.\n4. Verify the answer with an example.\n\n**Tip:** Configure the Groq key only on the backend `.env` file to enable live AI answers.'''


def quiz(subject, topic, difficulty, n=5):
    prompt = f'''Create {n} multiple-choice questions on "{topic}" ({subject}), difficulty {difficulty}. Return ONLY a JSON array. Each object must contain question, options (4 strings), answer_index (0-3), explanation.'''
    raw = ask_llm([{'role': 'user', 'content': prompt}], system='Return strict JSON only. No markdown.', max_tokens=3000)
    if raw:
        try:
            raw = re.sub(r'```(?:json)?', '', raw).strip()
            data = json.loads(raw[raw.find('['):raw.rfind(']') + 1])
            valid = [q for q in data if len(q.get('options', [])) == 4 and isinstance(q.get('answer_index'), int)]
            if valid:
                return valid[:n]
        except Exception:
            pass
    return demo_quiz(subject, topic, difficulty, n)


def demo_quiz(subject, topic, difficulty, n):
    bank = [
        {'question': f'Which statement best describes {topic}?', 'options': [f'It is a core {subject} concept', 'It is only a hardware component', 'It is unrelated to learning', 'It has no practical use'], 'answer_index': 0, 'explanation': f'{topic} is treated here as a core topic in {subject}.'},
        {'question': f'What is a good first step when studying {topic}?', 'options': ['Understand the basic definition', 'Skip directly to advanced problems', 'Memorize without examples', 'Avoid practice'], 'answer_index': 0, 'explanation': 'Strong learning starts with the concept, then examples and practice.'},
        {'question': f'Which strategy improves retention of {topic}?', 'options': ['Active recall and practice', 'Reading once only', 'Ignoring mistakes', 'Studying without breaks'], 'answer_index': 0, 'explanation': 'Active recall and spaced practice improve retention.'},
        {'question': f'When solving a problem on {topic}, what should you check?', 'options': ['Assumptions and steps', 'Only the final number', 'The font used', 'Nothing'], 'answer_index': 0, 'explanation': 'Checking assumptions and intermediate steps helps catch errors.'},
        {'question': f'What indicates mastery of {topic}?', 'options': ['Explaining it and solving new problems', 'Copying one example', 'Avoiding questions', 'Memorizing a title'], 'answer_index': 0, 'explanation': 'Mastery is demonstrated by explanation and transfer to new problems.'}
    ]
    return bank[:n]
