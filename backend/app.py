from __future__ import annotations
import os
import base64
import time
from fastapi import Request
from collections import OrderedDict
from threading import BoundedSemaphore, Lock
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .so101 import SO101Simulation as Simulation
from .planner import plan_instruction, plan_instruction_local, validate_instruction, PlanRejected

app=FastAPI(title='Granted Robotics',version='1.0.0',description='Auditable bimanual MuJoCo simulation. Not a physical robot controller.')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173,http://localhost:4173,https://granted-ai-2026.web.app,https://granted-ai-2026.firebaseapp.com,https://granted-robotics.web.app,https://granted-robotics.firebaseapp.com,http://127.0.0.1:5173,http://127.0.0.1:4173').split(','),allow_methods=['GET','POST'],allow_headers=['Content-Type','Authorization'])
class RunRequest(BaseModel):
    instruction:str=Field(default='Set the table with a cup and bowl',min_length=3,max_length=500)
    fault:Literal['none','object_displaced','grip_loss','obstacle']='none'
    seed:int=Field(default=42,ge=0,le=2147483647)
    recovery:bool=True
    recovery_enabled:bool | None=None
runs=OrderedDict()
lock=Lock()
capacity=BoundedSemaphore(2)
rate_windows={}
llm_calls=0
@app.get('/api/health')
def health():
    import mujoco
    try:
        import openvino
        ov=openvino.__version__
    except ImportError: ov=None
    return {'status':'ok','engine':'MuJoCo '+mujoco.__version__,'openvino':ov,'planner':'OpenAI with constrained schema' if os.getenv('OPENAI_API_KEY') else 'deterministic structured task planner','hardware':'simulation only','persistence':'last 30 runs in server memory'}
@app.post('/api/runs')
def create_run(request:RunRequest, http_request:Request):
    global llm_calls
    try:validate_instruction(request.instruction)
    except PlanRejected as exc:raise HTTPException(422,str(exc)) from exc
    address=http_request.client.host if http_request.client else "unknown"
    now=time.monotonic()
    with lock:
        recent=[t for t in rate_windows.get(address,[]) if now-t<60]
        if len(recent)>=12:raise HTTPException(429,"Limit reached: 12 runs per minute. Please wait.")
        rate_windows[address]=recent+[now]
        if len(rate_windows)>1000:rate_windows.clear()
    if not capacity.acquire(blocking=False): raise HTTPException(429,'Simulation workers are busy. Please retry shortly.')
    try:
        simulation=Simulation(request.seed)
        observation=None
        with lock:
            use_llm=bool(os.getenv('OPENAI_API_KEY')) and llm_calls<int(os.getenv('MAX_LLM_CALLS','300'))
            if use_llm:llm_calls+=1
        if use_llm:
            try: observation=simulation.render_png()
            except Exception: observation=None
        try: plan=plan_instruction(request.instruction,observation) if use_llm else plan_instruction_local(request.instruction)
        except PlanRejected as exc: raise HTTPException(422,str(exc)) from exc
        recovery=request.recovery if request.recovery_enabled is None else request.recovery_enabled
        result=simulation.run(request.instruction,request.fault,recovery)
        result['planner']=plan['source'];result['language_plan']=plan
        result['observation_image']=('data:image/png;base64,'+base64.b64encode(observation).decode()) if observation else None
        result['camera_observation']=('rendered MuJoCo RGB validated by language model' if plan.get('vision_input') else 'provider unavailable; deterministic task executed without vision validation' if observation else 'not used')
        with lock:
            runs[result['id']]=result
            while len(runs)>30: runs.popitem(last=False)
        return result
    finally: capacity.release()
@app.get('/api/runs/{run_id}')
def get_run(run_id:str):
    with lock: result=runs.get(run_id)
    if result is None: raise HTTPException(404,'Run not found or expired. Export traces to retain evidence.')
    return result
