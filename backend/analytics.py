import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
WEAK=60; STRONG=80

def frame(rows):
    df=pd.DataFrame(rows)
    if df.empty: return pd.DataFrame(columns=['id','subject','topic','difficulty','score','total','taken_at','percent'])
    df['percent']=df['score']/df['total']*100
    return df

def stats(df):
    if df.empty: return {'quizzes':0,'avg':0,'best':0,'latest':0,'streak':0}
    return {'quizzes':len(df),'avg':float(df.percent.mean()),'best':float(df.percent.max()),'latest':float(df.percent.iloc[-1]),'streak':min(len(df),7)}

def topics(df):
    if df.empty:return []
    g=df.assign(topic=df.topic.str.strip().str.title()).groupby(['subject','topic']).agg(avg=('percent','mean'),attempts=('percent','count')).reset_index()
    g['status']=g.avg.apply(lambda x:'Weak' if x<WEAK else ('Strong' if x>=STRONG else 'Average'))
    return g.sort_values('avg').to_dict('records')

def recommendations(df):
    if df.empty:return ['Take your first quiz to unlock personalised recommendations.']
    t=topics(df); out=[]
    for r in t:
        if r['status']=='Weak': out.append(f"Revise **{r['topic']}** ({r['subject']}) — average {r['avg']:.0f}%. Then retake a focused quiz.")
        elif r['status']=='Average': out.append(f"Practice **{r['topic']}** ({r['subject']}) — {r['avg']:.0f}%. Try a harder quiz next.")
    return out or ['Excellent! Your tracked topics are strong. Try Hard difficulty to keep progressing.']

def prediction(df):
    if len(df)<3:return None
    model=LinearRegression().fit(np.arange(len(df)).reshape(-1,1),df.percent.values)
    return round(float(np.clip(model.predict([[len(df)]])[0],0,100)),1)
