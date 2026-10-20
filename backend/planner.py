from .ai_engine import ask_llm

def build(weak, days, hours, goal=''):
    topics=', '.join(f"{x['topic']} ({x['subject']}, {x['avg']:.0f}%)" for x in weak) or 'No weak topics detected'
    prompt=f'''Create a polished {days}-day study plan with {hours} hours/day. Weak topics: {topics}. Goal: {goal or 'general improvement'}. Format each day with time blocks for concept learning, practice, quiz and review. Prioritise weak topics.'''
    ai=ask_llm([{'role':'user','content':prompt}],max_tokens=1800)
    if ai:return ai
    lines=[]
    for d in range(1,days+1):
        t=weak[(d-1)%len(weak)]['topic'] if weak else 'Mixed Revision'
        lines.append(f'### Day {d}\n**{hours}h:** 45% {t} concepts · 35% practice · 10% quiz · 10% review\n\n**Focus:** Write 3 key takeaways and one question you still have.')
    return '\n\n'.join(lines)
