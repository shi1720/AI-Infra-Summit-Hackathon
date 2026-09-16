"""Exercise the deployed application contract without printing credentials."""
import json, time, urllib.request, urllib.error, pathlib
BASE='https://granted-robotics.web.app'
results=[]
for instruction,fault,recovery,expected in [
 ('Set the table with a cup and bowl','none',True,'completed'),
 ('Set the table with a cup and bowl','grip_loss',True,'completed'),
 ('Set the table with a cup and bowl','grip_loss',False,'failed'),
 ('Set the table with a cup and bowl','obstacle',True,'blocked'),
 ('Put the cup on the floor','none',True,'rejected'),
]:
 start=time.time()
 payload={'instruction':instruction,'fault':fault,'seed':42,'recovery':recovery}
 req=urllib.request.Request(BASE+'/api/runs',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as response: data=json.load(response)
  actual=data['status']; row={'expected':expected,'actual':actual,'fault':fault,'recovery':recovery,'metrics':data['metrics'],'planner':data['planner'],'language_plan':data.get('language_plan'),'policy':data.get('policy'),'seconds':round(time.time()-start,2)}
 except urllib.error.HTTPError as exc:
  body=exc.read().decode();actual='rejected' if exc.code==422 else 'http_error';row={'expected':expected,'actual':actual,'http_status':exc.code,'detail':body,'seconds':round(time.time()-start,2)}
 results.append(row);print(json.dumps(row),flush=True)
 assert actual==expected, f'{expected}: received {actual}'
pathlib.Path('deliverables/deployed-smoke-tests.json').write_text(json.dumps({'base_url':BASE,'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'tests':results},indent=2))
print('PASS: all five live deployment checks',flush=True)
