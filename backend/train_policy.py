"""Generate SO101 IK demonstrations and train a small imitation baseline."""
import argparse,json,time
from pathlib import Path
import numpy as np
from .policy import MODEL_DIR,features,export_openvino
from .so101 import SO101Simulation,BASES

def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=600);a=p.parse_args()
    rng=np.random.default_rng(1720);sim=SO101Simulation(42,use_policy=False);xs=[];ys=[]
    began=time.perf_counter()
    for i in range(a.samples):
        relative=np.array([rng.uniform(.22,.405),rng.uniform(-.13,.13),rng.uniform(.025,.17)])
        point=relative+np.array(BASES['left']);point[2]=relative[2]
        try:q=sim.solve_ik('left',point)
        except ValueError:continue
        xs.append(relative);ys.append(q)
    x=np.array(xs);y=np.array(ys);cut=int(len(x)*.8)
    phi=features(x[:cut]);regularizer=np.eye(phi.shape[1])*.001
    weights=np.linalg.solve(phi.T@phi+regularizer,phi.T@y[:cut])
    prediction=features(x[cut:])@weights
    err=prediction-y[cut:]
    MODEL_DIR.mkdir(parents=True,exist_ok=True)
    np.save(MODEL_DIR/'weights.npy',weights.astype(np.float32))
    np.savez_compressed(MODEL_DIR/'demonstrations.npz',relative_target_xyz=x,joint_target=y,split_index=cut)
    export_openvino(weights)
    report={'model':'degree-4 polynomial joint-target imitation policy','teacher':'SO101 damped least-squares inverse kinematics','training_samples':cut,'heldout_samples':len(x)-cut,'seed':1720,'heldout_joint_rmse_rad':float(np.sqrt(np.mean(err**2))),'heldout_joint_mae_rad':float(np.mean(abs(err))),'training_seconds':time.perf_counter()-began,'deployment':'OpenVINO CPU FP32; prediction initializes mandatory numerical pose correction','limitations':'Learns local IK mapping, not vision or language. No task success is claimed from joint prediction error alone.'}
    (MODEL_DIR/'training-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
