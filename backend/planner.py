"""Constrained task planning. Unknown objects and locations fail closed."""
from __future__ import annotations
import base64
import json
import os
import re
import urllib.error
import urllib.request

class PlanRejected(ValueError):
    """The requested or generated plan is outside the workcell contract."""

# A small, explicit natural-language grammar is the offline contract. The model
# can validate the camera scene; it cannot expand the motion capability set.
_TASK_PATTERNS = [
    r'(?:set|prepare|arrange) (?:the |a )?table(?: for (?:breakfast|dinner|a meal))?(?: with (?:a |the )?cup and (?:a |the )?bowl)?',
    r'(?:move|place|put|arrange) (?:the |a )?cup and (?:the |a )?bowl(?: to their serving positions| at their serving positions| in their serving positions| on the table| for breakfast| for dinner)?',
]

def validate_instruction(instruction):
    text=' '.join(instruction.strip().lower().split())
    text=re.sub(r'^please\s+','',text)
    text=re.sub(r'\.?\s*keep the two arms safely separated\.?$','',text)
    text=text.rstrip('.!').strip()
    if not any(re.fullmatch(pattern,text) for pattern in _TASK_PATTERNS):
        raise PlanRejected('Unsupported task. This workcell can only place one cup and one bowl at their predefined serving positions. Try: "Set the table with a cup and bowl". Alternate objects, quantities and locations are not supported.')

def plan_instruction_local(instruction):
    return plan_instruction(instruction,allow_provider=False)

def plan_instruction(instruction,observation_png=None,allow_provider=True):
    validate_instruction(instruction)
    text=instruction.strip()
    result={'task':'table_setting','objects':['cup','bowl'],'order':'parallel','source':'deterministic structured task planner','model':None,'vision_input':False,'provider_status':'not_used'}
    key=os.environ.get('OPENAI_API_KEY') if allow_provider else None
    if not key:return result
    content=[{'type':'text','text':text}]
    if observation_png:
        content.append({'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(observation_png).decode(),'detail':'low'}})
    payload={'model':os.environ.get('OPENAI_MODEL','gpt-4o-mini'),'messages':[{'role':'system','content':'Validate a fixed robotics task. The only task is table_setting with objects cup and bowl and order parallel, at predefined serving positions. If supplied an image, The camera depicts a deliberately simplified robotics simulation, not photorealistic tableware. A SOLID ORANGE CYLINDER is the cup proxy and a SOLID BLUE CYLINDER is the bowl proxy; handles, hollow interiors and realistic bowl shapes are not expected. The two yellow articulated structures are SO101 robot arms. Approve this known workcell if both colored object proxies and robot arms are visible. Do not reject merely because the objects look like cylinders. Reject an unrelated or empty image. Output JSON only: supported (boolean), reason (short string), task (table_setting), objects ([cup,bowl]), order (parallel). Do not expand capabilities.'},{'role':'user','content':content}],'response_format':{'type':'json_object'},'temperature':0,'max_tokens':220}
    request=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=15) as response:data=json.load(response)
    except (ValueError,TypeError) as exc:
        raise PlanRejected('Language provider returned malformed JSON. No motion was executed.') from exc
    except (urllib.error.URLError,TimeoutError,OSError):
        # The exact task has already passed the local grammar. Provider failure
        # never changes its objects, destinations or safety envelope.
        return {**result,'source':'deterministic fallback (language provider unavailable)','provider_status':'unavailable'}
    try:
        parsed=json.loads(data['choices'][0]['message']['content'])
        objects=parsed.get('objects')
        valid_objects=isinstance(objects,list) and len(objects)==2 and all(isinstance(v,str) for v in objects) and set(objects)=={'cup','bowl'}
        if parsed.get('supported') is not True:
            raise PlanRejected('Scene validation rejected: '+str(parsed.get('reason','The image did not match the supported workcell'))[:250])
        if parsed.get('task')!='table_setting' or not valid_objects or parsed.get('order')!='parallel':
            raise PlanRejected('Planner output did not pass the allowed task schema.')
    except (KeyError,TypeError,ValueError,AttributeError) as exc:
        if isinstance(exc,PlanRejected):raise
        raise PlanRejected('Language provider returned a malformed plan. No motion was executed.') from exc
    return {**result,'source':'OpenAI constrained language planner','model':payload['model'],'vision_input':bool(observation_png),'provider_status':'validated','reason':str(parsed.get('reason',''))[:300]}
