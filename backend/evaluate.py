"""Reproducible matched-seed ablation of recovery and fault behavior."""
import argparse
import json
import platform
from pathlib import Path
import numpy as np
from .so101 import SO101Simulation
from .simulation import SafetyMonitor

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seeds',type=int,default=10);parser.add_argument('--output',default='backend/evidence/evaluation.json');args=parser.parse_args()
    results=[]
    for seed in range(args.seeds):
        for fault,recovery in [('none',True),('object_displaced',True),('grip_loss',True),('grip_loss',False),('obstacle',True)]:
            run=SO101Simulation(seed).run('Set the table with a cup and bowl',fault,recovery)
            results.append({k:run[k] for k in ['seed','fault','recovery_enabled','status','metrics','perturbations']})
    groups={}
    for fault,recovery in [('none',True),('object_displaced',True),('grip_loss',True),('grip_loss',False),('obstacle',True)]:
        rows=[r for r in results if r['fault']==fault and r['recovery_enabled']==recovery]
        groups[f'{fault}:recovery={recovery}']={'runs':len(rows),'completed':sum(r['status']=='completed' for r in rows),'blocked':sum(r['status']=='blocked' for r in rows),'mean_cup_error_mm':round(float(np.mean([r['metrics']['placement_error_mm']['cup'] for r in rows])),2),'mean_compute_ms':round(float(np.mean([r['metrics']['compute_ms'] for r in rows])),2)}
    monitor=SafetyMonitor();rng=np.random.default_rng(5);errors=[]
    for _ in range(1100):
        x=rng.uniform(-1,1,(2,3)).astype(np.float32);value=monitor.distance(x);errors.append(abs(value-float(np.linalg.norm(x[0]-x[1]))))
    times=monitor.latencies[100:]
    result={'robot':'MuJoCo Menagerie dual SO101','host':{'platform':platform.platform(),'processor':platform.machine(),'intel_hardware':False},'seed_count':args.seeds,'total_runs':len(results),'randomization':'Each object: +/-8 mm XY, mass and sliding friction 0.8x to 1.2x, cylinder radius/height 0.92x to 1.08x. Light diffuse/ambient and table background RGB also vary. No alternate shape families.','groups':groups,'monitor_benchmark':{'engine':monitor.engine,'precision':'FP32 input and FP32 inference precision hint','warmup':100,'samples':1000,'p50_ms':round(float(np.percentile(times,50)),5),'p95_ms':round(float(np.percentile(times,95)),5),'serial_inferences_per_second':round(1000/float(np.mean(times)),1),'max_abs_distance_error_m':max(errors),'scope':'Geometric separation graph only, not end-to-end VLA or Intel hardware benchmark'},'runs':results}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))
if __name__=='__main__':main()
