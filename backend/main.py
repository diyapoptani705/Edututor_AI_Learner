import os
import secrets
from dotenv import load_dotenv

# Load secrets only in the backend process. The frontend never receives the API key.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import db, analytics
from .ai_engine import tutor, quiz
from .planner import build

db.init_db()
app=FastAPI(title='EduTutor AI API', version='2.0.0', description='Backend for the EduTutor personalized learning assistant.')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

class Register(BaseModel): username:str; password:str; full_name:str; grade:str
class Login(BaseModel): username:str; password:str
class TutorReq(BaseModel): question:str; subject:str; grade:str; history:list[dict]=[]
class QuizReq(BaseModel): subject:str; topic:str; difficulty:str; n:int=Field(5,ge=3,le=10)
class QuizSubmit(BaseModel): subject:str; topic:str; difficulty:str; score:int; total:int
class PlanReq(BaseModel): days:int=Field(7,ge=1,le=30); hours:int=Field(2,ge=1,le=8); goal:str=''

def current_user(authorization:Optional[str]):
    token=(authorization or '').replace('Bearer ','').strip()
    u=db.user_for_token(token)
    if not u: raise HTTPException(401,'Please log in again.')
    return u

@app.get('/api/health')
def health(): return {'status':'ok','service':'EduTutor AI API'}

@app.post('/api/auth/register')
def register(x:Register):
    try: uid=db.create_user(x.username,x.password,x.full_name,x.grade)
    except ValueError as e: raise HTTPException(400,str(e))
    return {'message':'Account created successfully.','user_id':uid}

@app.post('/api/auth/login')
def login(x:Login):
    u=db.authenticate(x.username,x.password)
    if not u: raise HTTPException(401,'Invalid username or password.')
    token=secrets.token_urlsafe(32); db.save_session(token,u['id'])
    return {'token':token,'user':{'id':u['id'],'username':u['username'],'full_name':u['full_name'],'grade':u['grade']}}

@app.post('/api/auth/logout')
def logout(authorization:Optional[str]=Header(None)):
    token=(authorization or '').replace('Bearer ','').strip(); db.delete_session(token); return {'ok':True}

@app.get('/api/dashboard')
def dashboard(authorization:Optional[str]=Header(None)):
    u=current_user(authorization); df=analytics.frame(db.quiz_rows(u['id']))
    return {'stats':analytics.stats(df),'topics':analytics.topics(df),'recommendations':analytics.recommendations(df),'prediction':analytics.prediction(df),'history':df.to_dict('records')}

@app.post('/api/tutor')
def tutor_api(x:TutorReq, authorization:Optional[str]=Header(None)):
    u=current_user(authorization); answer=tutor(x.question,x.subject,x.grade,x.history); db.save_chat(u['id'],x.subject,x.question,answer); return {'answer':answer}

@app.get('/api/tutor/history')
def history(authorization:Optional[str]=Header(None)):
    return {'items':db.chats(current_user(authorization)['id'])}

@app.post('/api/quiz/generate')
def quiz_api(x:QuizReq, authorization:Optional[str]=Header(None)):
    current_user(authorization); return {'quiz':quiz(x.subject,x.topic,x.difficulty,x.n)}

@app.post('/api/quiz/submit')
def submit(x:QuizSubmit, authorization:Optional[str]=Header(None)):
    u=current_user(authorization); db.save_quiz(u['id'],x.subject,x.topic,x.difficulty,x.score,x.total); return {'percent':round(x.score/x.total*100,1)}

@app.post('/api/planner')
def planner_api(x:PlanReq, authorization:Optional[str]=Header(None)):
    u=current_user(authorization); df=analytics.frame(db.quiz_rows(u['id'])); text=build(analytics.topics(df),x.days,x.hours,x.goal); db.save_plan(u['id'],text); return {'plan':text}

@app.get('/api/planner/latest')
def latest(authorization:Optional[str]=Header(None)):
    p=db.latest_plan(current_user(authorization)['id']); return {'plan':p}
