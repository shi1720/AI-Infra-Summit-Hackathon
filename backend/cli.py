import argparse
import json
from pathlib import Path
from .so101 import SO101Simulation as Simulation
from .planner import plan_instruction

def main():
    parser=argparse.ArgumentParser(description='Run the Granted MuJoCo workbench')
    parser.add_argument('--instruction',default='Set the table with a cup and bowl')
    parser.add_argument('--fault',choices=['none','object_displaced','grip_loss','obstacle'],default='none')
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--no-recovery',action='store_true')
    parser.add_argument('--output',default='artifacts/run.json')
    args=parser.parse_args()
    plan=plan_instruction(args.instruction)
    result=Simulation(args.seed).run(args.instruction,args.fault,not args.no_recovery)
    result['planner']=plan['source'];result['language_plan']=plan
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2))
    print(json.dumps({'status':result['status'],'metrics':result['metrics'],'output':str(path)},indent=2))
if __name__=='__main__':main()
