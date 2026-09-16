"""Compare a learned OpenVINO action proposal plus IK correction with IK alone."""
import json,platform,argparse
from pathlib import Path
import numpy as np
from .so101 import SO101Simulation
from .policy import JointPolicy,features,MODEL_DIR

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='backend/evidence/policy-evaluation.json');args=parser.parse_args()
    rows=[]
    for seed in range(10):
        for learned in [False,True]:
            sim=SO101Simulation(seed,use_policy=learned);run=sim.run('Set the table','grip_loss')
            rows.append({'seed':seed,'learned':learned,'status':run['status'],'metrics':run['metrics'],'policy':run['policy']})
    groups={}
    for learned in [False,True]:
        r=[v for v in rows if v['learned']==learned]
        groups['learned_plus_correction' if learned else 'ik_only']={'successes':sum(v['status']=='completed' for v in r),'trials':len(r),'mean_ik_iterations':float(np.mean([v['metrics']['ik_iterations'] for v in r])),'mean_compute_ms':float(np.mean([v['metrics']['compute_ms'] for v in r])),'mean_cup_error_mm':float(np.mean([v['metrics']['placement_error_mm']['cup'] for v in r]))}
    policy=JointPolicy();rng=np.random.default_rng(20);errors=[]
    for _ in range(1100):
        x=rng.uniform([.22,-.13,.025],[.405,.13,.17]);q=policy.predict(x);ref=features(x.astype(np.float32))@policy.weights;errors.append(float(np.max(abs(q-ref))))
    latency=policy.times[100:]
    result={'training':json.loads((MODEL_DIR/'training-report.json').read_text()),'host':platform.platform(),'groups':groups,'policy_benchmark':{'engine':policy.engine,'samples':1000,'warmup':100,'p50_ms':float(np.percentile(latency,50)),'p95_ms':float(np.percentile(latency,95)),'serial_inferences_per_second':1000/float(np.mean(latency)),'max_abs_vs_numpy_rad':max(errors)},'limitations':'Learned joint-target proposals initialize numerical pose correction. Success includes that correction, not unassisted learned control. Camera and language validation are separate from this state-based imitation policy.','runs':rows}
    Path(args.output).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))
if __name__=='__main__':main()
