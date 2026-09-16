"""Small learned joint-target imitation policy with OpenVINO inference.

This is supervised polynomial regression distilled from numerical SO101 IK.
It proposes joint targets. A numerical pose correction and the existing safety
checks remain mandatory. It is not a pretrained vision-language-action model.
"""
from pathlib import Path
import json,time
import numpy as np

MODEL_DIR=Path(__file__).parent/'assets'/'joint_policy'
MEAN=np.array([.31,0.,.10],dtype=np.float32)
SCALE=np.array([.1,.15,.1],dtype=np.float32)
POWERS=[(i,j,k) for i in range(5) for j in range(5-i) for k in range(5-i-j)]

def features(x):
    z=(np.asarray(x)-MEAN)/SCALE
    return np.stack([np.prod(z**np.array(p),axis=-1) for p in POWERS],axis=-1)

class JointPolicy:
    def __init__(self,device="CPU"):
        self.compiled=None;self.times=[];self.engine='unavailable'
        path=MODEL_DIR/'weights.npy'
        if not path.exists():return
        self.weights=np.load(path,allow_pickle=False)
        try:
            import openvino as ov
            self.compiled=ov.Core().compile_model(str(MODEL_DIR/'policy.xml'),device,{'INFERENCE_PRECISION_HINT':'f32'})
            self.engine='OpenVINO '+device+' learned polynomial imitation policy (FP32)'
        except (ImportError,RuntimeError):self.engine='NumPy learned polynomial imitation policy'
    @property
    def available(self):return hasattr(self,'weights')
    def predict(self,point):
        start=time.perf_counter();x=np.asarray(point,dtype=np.float32).reshape(1,3)
        q=self.compiled([x])[0][0] if self.compiled else (features(x)@self.weights)[0]
        self.times.append((time.perf_counter()-start)*1000)
        return np.asarray(q,dtype=float)

def export_openvino(weights):
    import openvino as ov
    from openvino import opset13 as op
    x=op.parameter([1,3],np.float32,name='relative_target_xyz')
    z=op.divide(op.subtract(x,op.constant(MEAN)),op.constant(SCALE))
    columns=[]
    for p in POWERS:
        powered=op.power(z,op.constant(np.array(p,dtype=np.float32)))
        columns.append(op.reduce_prod(powered,op.constant([1]),True))
    phi=op.concat(columns,1)
    y=op.matmul(phi,op.constant(weights.astype(np.float32)),False,False)
    model=ov.Model([y],[x],'SO101_joint_target_imitation')
    ov.save_model(model,str(MODEL_DIR/'policy.xml'),compress_to_fp16=False)
