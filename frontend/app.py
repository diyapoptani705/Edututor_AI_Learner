import os, requests, streamlit as st
import pandas as pd
import plotly.express as px

API=os.getenv('EDUTUTOR_API_URL','http://127.0.0.1:8000/api')
SUBJECTS=['Mathematics','Physics','Chemistry','Biology','Computer Science','English','History','Geography','Economics','Other']
LEVELS=['School (8-10)','School (11-12)','Undergraduate','Postgraduate']

st.set_page_config(page_title='EduTutor AI',page_icon='🎓',layout='wide',initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:linear-gradient(135deg,#f7f9ff 0%,#eef2ff 52%,#f9fbff 100%)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#111936 0%,#17245a 100%);border-right:1px solid #27356e}
[data-testid="stSidebar"] *{color:#f5f7ff!important}
[data-testid="stSidebar"] .stRadio label{padding:9px 10px;border-radius:10px}
[data-testid="stSidebar"] .stRadio label:hover{background:#24346e}
.hero{padding:28px 32px;border-radius:24px;background:linear-gradient(120deg,#17245a,#4f46e5 58%,#7c3aed);color:white;box-shadow:0 18px 50px rgba(55,65,180,.22);margin-bottom:24px}
.hero h1{font-size:38px;line-height:1.1;margin:0 0 8px;font-weight:800}.hero p{margin:0;color:#dfe5ff;font-size:15px}
.eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#aab6ff;margin-bottom:8px}
.card{background:rgba(255,255,255,.88);border:1px solid #e4e8f5;border-radius:18px;padding:20px;box-shadow:0 8px 30px rgba(30,41,90,.06);height:100%}
.metric{background:#fff;border:1px solid #e4e8f5;border-radius:16px;padding:18px 20px;box-shadow:0 7px 24px rgba(30,41,90,.06)}
.metric .label{font-size:12px;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:.06em}.metric .value{font-size:30px;font-weight:800;color:#17245a;margin-top:4px}.metric .sub{font-size:12px;color:#64748b;margin-top:3px}
.pill{display:inline-block;padding:5px 10px;border-radius:999px;background:#eef2ff;color:#4338ca;font-size:11px;font-weight:800}
.section-title{font-size:21px;font-weight:800;color:#17245a;margin:12px 0 12px}.muted{color:#64748b;font-size:13px}
div.stButton>button{border-radius:11px;border:0;background:linear-gradient(90deg,#4f46e5,#7c3aed);color:white;font-weight:700;min-height:42px;box-shadow:0 7px 18px rgba(79,70,229,.20)}
div.stButton>button:hover{background:linear-gradient(90deg,#4338ca,#6d28d9);color:white}
.stTextInput>div>div,.stSelectbox>div>div,.stNumberInput>div>div,.stTextArea>div>div{border-radius:11px}
[data-testid="stChatMessage"]{border-radius:16px;border:1px solid #e4e8f5;background:white}
.auth-wrap{max-width:980px;margin:60px auto}.auth-card{background:white;border:1px solid #e4e8f5;border-radius:24px;padding:34px;box-shadow:0 20px 60px rgba(30,41,90,.12)}
.small-note{font-size:12px;color:#64748b;text-align:center;margin-top:14px}
</style>''',unsafe_allow_html=True)

def req(method,path,**kwargs):
    headers=kwargs.pop('headers',{})
    if st.session_state.get('token'): headers['Authorization']='Bearer '+st.session_state.token
    try:
        r=requests.request(method,API+path,headers=headers,timeout=60,**kwargs)
        if r.status_code>=400: return None, r.json().get('detail','Request failed.')
        return r.json(),None
    except requests.RequestException as e: return None,f'Backend unavailable: {e}'

def logout():
    req('POST','/auth/logout'); st.session_state.clear(); st.rerun()

def auth():
    st.markdown('<div class="auth-wrap"><div class="hero"><div class="eyebrow">AI-powered learning workspace</div><h1>EduTutor AI 🎓</h1><p>Personalized explanations, smart quizzes, performance insights and study planning — in one focused dashboard.</p></div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.1,.9])
    with left:
        st.markdown('<div class="auth-card"><div class="section-title">Welcome back</div><div class="muted">Sign in to continue your learning journey.</div>',unsafe_allow_html=True)
        with st.form('login'):
            u=st.text_input('Username'); p=st.text_input('Password',type='password')
            if st.form_submit_button('Sign in →',use_container_width=True):
                data,err=req('POST','/auth/login',json={'username':u,'password':p})
                if err: st.error(err)
                else: st.session_state.token=data['token']; st.session_state.user=data['user']; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="auth-card"><div class="section-title">Create account</div><div class="muted">Set up your personalized student profile.</div>',unsafe_allow_html=True)
        with st.form('register'):
            name=st.text_input('Full name'); grade=st.selectbox('Class / level',LEVELS); u2=st.text_input('Choose username'); p2=st.text_input('Choose password',type='password')
            if st.form_submit_button('Create account',use_container_width=True):
                data,err=req('POST','/auth/register',json={'username':u2,'password':p2,'full_name':name,'grade':grade})
                if err: st.error(err)
                else: st.success(data['message']+' You can sign in now.')
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="small-note">Your quiz history, tutor chats and plans are stored in the SQLite backend.</div>',unsafe_allow_html=True)

if 'token' not in st.session_state:
    auth(); st.stop()

user=st.session_state.user
with st.sidebar:
    st.markdown('<div style="font-size:28px;font-weight:800;margin-bottom:4px">🎓 EduTutor</div><div style="color:#aab6ff!important;font-size:12px">PERSONALIZED LEARNING OS</div>',unsafe_allow_html=True)
    st.divider()
    st.markdown(f'<div style="padding:12px;background:#202e64;border-radius:14px;margin-bottom:14px"><b>{user["full_name"]}</b><br><span style="font-size:12px;color:#cbd5ff!important">{user["grade"]}</span></div>',unsafe_allow_html=True)
    page=st.radio('Workspace',['Overview','AI Tutor','Smart Quiz','Recommendations','Study Planner'],label_visibility='collapsed')
    st.divider(); st.caption('EduTutor AI v2.0')
    if st.button('Sign out',use_container_width=True): logout()

data,err=req('GET','/dashboard')
if err:
    st.error(err); st.stop()
stats=data['stats']; topics=data['topics']; history=data['history']

if page=='Overview':
    st.markdown(f'<div class="hero"><div class="eyebrow">Good to see you, {user["full_name"].split()[0]} 👋</div><h1>Your learning command center</h1><p>Track progress, identify weak areas and keep your study plan moving forward.</p></div>',unsafe_allow_html=True)
    cols=st.columns(4)
    cards=[('QUIZZES TAKEN',stats['quizzes'],'Total attempts'),('AVERAGE SCORE',f"{stats['avg']:.0f}%",'Across all quizzes'),('BEST SCORE',f"{stats['best']:.0f}%",'Personal best'),('LATEST SCORE',f"{stats['latest']:.0f}%",'Most recent')]
    for c,(a,b,s) in zip(cols,cards):
        c.markdown(f'<div class="metric"><div class="label">{a}</div><div class="value">{b}</div><div class="sub">{s}</div></div>',unsafe_allow_html=True)
    st.write('')
    if history:
        c1,c2=st.columns([1.5,1])
        h=pd.DataFrame(history); h['Quiz']=range(1,len(h)+1)
        with c1:
            st.markdown('<div class="card"><div class="section-title">Score trajectory</div><div class="muted">Your performance over time</div>',unsafe_allow_html=True)
            fig=px.line(h,x='Quiz',y='percent',markers=True,range_y=[0,100],labels={'percent':'Score %'})
            fig.update_traces(line_width=4); fig.update_layout(height=300,margin=dict(l=10,r=10,t=20,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#475569')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card"><div class="section-title">Topic health</div><div class="muted">Weak areas need focused revision</div>',unsafe_allow_html=True)
            if topics:
                td=pd.DataFrame(topics); td['topic_label']=td['topic'].str.slice(0,18)
                fig2=px.bar(td.sort_values('avg'),x='avg',y='topic_label',orientation='h',range_x=[0,100],labels={'avg':'Avg %','topic_label':''})
                fig2.update_layout(height=300,margin=dict(l=10,r=10,t=20,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#475569',showlegend=False)
                st.plotly_chart(fig2,use_container_width=True,config={'displayModeBar':False})
            else: st.info('Take a quiz to unlock topic analytics.')
            st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recent activity</div>',unsafe_allow_html=True)
        show=h.sort_values('taken_at',ascending=False).head(6)[['taken_at','subject','topic','difficulty','score','total','percent']]
        show.columns=['Date','Subject','Topic','Difficulty','Score','Total','Percent']
        st.dataframe(show,use_container_width=True,hide_index=True)
    else:
        st.markdown('<div class="card" style="text-align:center;padding:45px"><div style="font-size:42px">🚀</div><div class="section-title">Your dashboard is ready</div><div class="muted">Start with a Smart Quiz to create your first performance data.</div></div>',unsafe_allow_html=True)

elif page=='AI Tutor':
    st.markdown('<div class="hero"><div class="eyebrow">Module 1 · AI Tutor</div><h1>Ask. Understand. Master. 🤖</h1><p>Get step-by-step explanations tailored to your academic level.</p></div>',unsafe_allow_html=True)
    c1,c2=st.columns([.65,.35]); subject=c1.selectbox('Subject',SUBJECTS); st.session_state.setdefault('chat',[])
    with c2: st.markdown('<div class="card"><b>Study mode</b><br><span class="muted">Clear explanations · Examples · Takeaways</span></div>',unsafe_allow_html=True)
    for m in st.session_state.chat:
        with st.chat_message(m['role']): st.markdown(m['content'])
    q=st.chat_input('Ask a doubt, formula, concept or example...')
    if q:
        with st.chat_message('user'): st.markdown(q)
        data2,err=req('POST','/tutor',json={'question':q,'subject':subject,'grade':user['grade'],'history':st.session_state.chat})
        ans=err or data2['answer']
        st.session_state.chat += [{'role':'user','content':q},{'role':'assistant','content':ans}]
        with st.chat_message('assistant'): st.markdown(ans)
    with st.expander('Recent saved questions'):
        hh,_=req('GET','/tutor/history')
        for x in (hh or {}).get('items',[]): st.markdown(f"**{x['subject']} · {x['asked_at']}** — {x['question']}\n\n{x['answer'][:220]}...")

elif page=='Smart Quiz':
    st.markdown('<div class="hero"><div class="eyebrow">Module 2 · Quiz Generator</div><h1>Turn revision into a challenge. 🧠</h1><p>Generate focused quizzes by subject, topic and difficulty — then feed the result into your analytics.</p></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns([1,1.4,1,0.7]); subject=c1.selectbox('Subject',SUBJECTS); topic=c2.text_input('Topic',placeholder='e.g. Newton’s Laws'); difficulty=c3.selectbox('Difficulty',['Easy','Medium','Hard']); n=c4.number_input('Questions',3,10,5)
    if st.button('✨ Generate smart quiz'):
        if not topic.strip(): st.warning('Enter a topic first.')
        else:
            d,e=req('POST','/quiz/generate',json={'subject':subject,'topic':topic.strip(),'difficulty':difficulty,'n':int(n)})
            if e: st.error(e)
            else: st.session_state.quiz=d['quiz']; st.session_state.quiz_meta=(subject,topic.strip(),difficulty)
    if st.session_state.get('quiz'):
        quiz=st.session_state.quiz; meta=st.session_state.quiz_meta
        st.markdown(f'<div class="card"><span class="pill">{meta[0]}</span> &nbsp; <span class="pill">{meta[2]}</span><div class="section-title">{meta[1]}</div><div class="muted">Choose the best answer for every question.</div></div>',unsafe_allow_html=True)
        with st.form('quizform'):
            ans=[]
            for i,q in enumerate(quiz): ans.append(st.radio(f'{i+1:02d}. {q["question"]}',q['options'],index=None,key=f'qa{i}'))
            submit=st.form_submit_button('Submit & analyze result',use_container_width=True)
        if submit:
            score=sum(1 for a,q in zip(ans,quiz) if a is not None and q['options'].index(a)==q['answer_index'])
            d,e=req('POST','/quiz/submit',json={'subject':meta[0],'topic':meta[1],'difficulty':meta[2],'score':score,'total':len(quiz)})
            pct=d['percent'] if d else score/len(quiz)*100
            st.success(f'🎉 Score: {score}/{len(quiz)} · {pct:.0f}%')
            for i,(a,q) in enumerate(zip(ans,quiz)):
                ok=a is not None and q['options'].index(a)==q['answer_index']
                st.markdown(f"{'✅' if ok else '❌'} **Q{i+1}** · Correct: **{q['options'][q['answer_index']]}**")
                st.caption(q.get('explanation',''))
            st.session_state.quiz=None

elif page=='Recommendations':
    st.markdown('<div class="hero"><div class="eyebrow">Modules 3 & 4 · Analytics</div><h1>Your next-best actions 🎯</h1><p>EduTutor detects weak areas and turns performance into practical revision guidance.</p></div>',unsafe_allow_html=True)
    if not topics: st.info('Take a few quizzes first. Your recommendations will appear here automatically.')
    else:
        weak=[x for x in topics if x['status']=='Weak']; avg=[x for x in topics if x['status']=='Average']; strong=[x for x in topics if x['status']=='Strong']
        a,b,c=st.columns(3)
        for col,title,num,desc in [(a,'Needs revision',len(weak),'Below 60%'),(b,'Keep practicing',len(avg),'60–79%'),(c,'Strong topics',len(strong),'80%+')]: col.markdown(f'<div class="metric"><div class="label">{title}</div><div class="value">{num}</div><div class="sub">{desc}</div></div>',unsafe_allow_html=True)
        st.write(''); st.markdown('<div class="section-title">Personalized recommendations</div>',unsafe_allow_html=True)
        for r in data['recommendations']: st.markdown(f'<div class="card" style="margin-bottom:10px">💡 {r}</div>',unsafe_allow_html=True)
        st.markdown('<div class="section-title">Topic performance</div>',unsafe_allow_html=True)
        td=pd.DataFrame(topics); td.columns=[c.title() if c not in ['avg','attempts'] else c for c in td.columns]; st.dataframe(td,use_container_width=True,hide_index=True)
        if weak and st.button('🤖 Explain my weakest topic'):
            w=weak[0]; d,e=req('POST','/tutor',json={'question':f'Give concise revision notes, key points and 2 examples for {w["topic"]}.','subject':w['subject'],'grade':user['grade'],'history':[]})
            if e: st.error(e)
            else: st.markdown(d['answer'])

elif page=='Study Planner':
    st.markdown('<div class="hero"><div class="eyebrow">Module 5 · Study Planner</div><h1>Build a plan you can actually follow. 📅</h1><p>Prioritize weak topics, divide your available time and keep revision structured.</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,2]); days=c1.slider('Days',1,30,7); hours=c2.slider('Hours/day',1,8,2); goal=c3.text_input('Exam / goal',placeholder='e.g. Prepare for Computer Networks exam')
    if st.button('✨ Generate personalized plan'):
        d,e=req('POST','/planner',json={'days':days,'hours':hours,'goal':goal})
        if e: st.error(e)
        else: st.session_state.plan=d['plan']
    if st.session_state.get('plan'):
        st.markdown('<div class="card">'+st.session_state.plan+'</div>',unsafe_allow_html=True)
    else:
        d,_=req('GET','/planner/latest')
        if d and d.get('plan'): st.markdown('<div class="card">'+d['plan']['plan_text']+'</div>',unsafe_allow_html=True)
        else: st.info('No plan yet. Set your available days and hours above to generate one.')
