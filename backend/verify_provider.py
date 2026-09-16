"""Manual integration check using the authorized deployment secret, never printed."""
import json,os,subprocess
from .planner import plan_instruction
from .so101 import SO101Simulation
if __name__=='__main__':
    secret=subprocess.run(['gcloud','secrets','versions','access','latest','--secret=granted-robotics-openai','--project=granted-ai-2026'],capture_output=True,text=True,check=True)
    os.environ['OPENAI_API_KEY']=secret.stdout.strip()
    sim=SO101Simulation();plan=plan_instruction('Set the table with a cup and bowl',sim.render_png())
    print(json.dumps(plan,indent=2))
