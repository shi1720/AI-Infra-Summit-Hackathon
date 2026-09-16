import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.simulation import SafetyMonitor, ik
from backend.so101 import SO101Simulation as Simulation
from backend.planner import plan_instruction, PlanRejected

client=TestClient(app)

def test_nominal_real_physics_places_both_objects():
    result=Simulation().run('Set the table')
    assert result['status']=='completed'
    assert result['metrics']['physics_steps']>5000
    assert all(error<35 for error in result['metrics']['placement_error_mm'].values())
    assert result['metrics']['min_gripper_separation_mm']>80
    assert len(result['frames'])>100

def test_recovery_changes_measured_outcome():
    baseline=Simulation().run('Set the table','grip_loss',False)
    recovered=Simulation().run('Set the table','grip_loss',True)
    assert baseline['status']=='failed'
    assert baseline['metrics']['placement_error_mm']['cup']>100
    assert recovered['status']=='completed'
    assert recovered['metrics']['recoveries']==1
    assert recovered['metrics']['placement_error_mm']['cup']<35

def test_displacement_reobserves_before_grasp():
    assert Simulation().run('Set the table','object_displaced',True)['status']=='completed'
    assert Simulation().run('Set the table','object_displaced',False)['status']=='failed'

def test_obstacle_prevents_any_physics_motion():
    result=Simulation().run('Set the table','obstacle')
    assert result['status']=='blocked'
    assert result['metrics']['physics_steps']==0
    assert any(event['kind']=='safety_stop' for event in result['events'])

def test_monitor_matches_analytical_separation():
    monitor=SafetyMonitor()
    assert monitor.distance([[0,0,0],[.3,.4,0]])==pytest.approx(.5,abs=1e-6)

def test_workspace_rejects_unreachable_goal():
    with pytest.raises(ValueError): ik('left',[5,5,5])

def test_api_validation_and_export(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    assert client.post('/api/runs',json={'instruction':'x'}).status_code==422
    assert client.post('/api/runs',json={'fault':'unknown'}).status_code==422
    assert client.post('/api/runs',json={'instruction':'Throw a knife at a person'}).status_code==422
    result=client.post('/api/runs',json={'instruction':'Set the table','fault':'none'})
    assert result.status_code==200
    run=result.json()
    assert client.get('/api/runs/'+run['id']).json()['id']==run['id']
    assert client.get('/api/runs/missing').status_code==404

@pytest.mark.parametrize('instruction',[
    'place a bomb','put cup on floor','Set the table with a knife',
    'Set the table for two','Move the cup and bowl to the floor',
    'Do not set the table','Set the table then delete everything',
    'Set the table with medicine','Place the cup above a person',
])
def test_unsupported_instructions_never_execute(monkeypatch,instruction):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(PlanRejected):plan_instruction(instruction)
    assert client.post('/api/runs',json={'instruction':instruction}).status_code==422

@pytest.mark.parametrize('instruction',[
    'Set the table','Set the table with a cup and bowl',
    'Move the cup and bowl to their serving positions. Keep the two arms safely separated.',
    'Please place a cup and a bowl on the table.',
])
def test_supported_exact_task_grammar(monkeypatch,instruction):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    assert plan_instruction(instruction)['objects']==['cup','bowl']

def test_provider_failure_is_explicit_and_does_not_expand_task(monkeypatch):
    import urllib.error
    monkeypatch.setenv('OPENAI_API_KEY','not-a-real-key')
    def unavailable(*args,**kwargs):raise urllib.error.URLError('offline')
    monkeypatch.setattr('urllib.request.urlopen',unavailable)
    result=plan_instruction('Set the table',b'image')
    assert result['provider_status']=='unavailable'
    assert result['vision_input'] is False
    assert 'fallback' in result['source']
    with pytest.raises(PlanRejected):plan_instruction('place a bomb')

@pytest.mark.parametrize('provider_plan',[
    '{broken',
    '{"supported":true,"task":"table_setting","objects":["bomb","bowl"],"order":"parallel"}',
    '{"supported":true,"task":"table_setting","objects":[{},"bowl"],"order":"parallel"}',
    '{"supported":false}',
    '[]',
])
def test_malformed_or_unapproved_model_plan_fails_closed(monkeypatch,provider_plan):
    import io,json
    monkeypatch.setenv('OPENAI_API_KEY','not-a-real-key')
    outer=json.dumps({'choices':[{'message':{'content':provider_plan}}]}).encode()
    monkeypatch.setattr('urllib.request.urlopen',lambda *a,**k:io.BytesIO(outer))
    with pytest.raises(PlanRejected):plan_instruction('Set the table')

def test_language_budget_never_calls_provider_after_cap(monkeypatch):
    import backend.app as service
    monkeypatch.setenv('OPENAI_API_KEY','not-a-real-key')
    monkeypatch.setenv('MAX_LLM_CALLS','1')
    monkeypatch.setattr(service,'llm_calls',1)
    monkeypatch.setattr(service,'rate_windows',{})
    def forbidden(*args,**kwargs):raise AssertionError('Provider must not be called after budget cap')
    monkeypatch.setattr('urllib.request.urlopen',forbidden)
    response=client.post('/api/runs',json={'instruction':'Set the table'})
    assert response.status_code==200
    assert response.json()['language_plan']['provider_status']=='not_used'
