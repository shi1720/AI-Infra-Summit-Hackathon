"""Benchmark the actual selected OpenVINO graph on CPU, GPU or NPU."""
import argparse,json,platform
from pathlib import Path
import numpy as np
import openvino as ov
from .simulation import SafetyMonitor
from .policy import JointPolicy,features

def main():
    p=argparse.ArgumentParser();p.add_argument('--device',choices=['CPU','GPU','NPU'],default='CPU');p.add_argument('--graph',choices=['policy','monitor'],default='policy');p.add_argument('--samples',type=int,default=1000);p.add_argument('--output',default='backend/evidence/device-benchmark.json');a=p.parse_args()
    core=ov.Core();available=core.available_devices
    if not any(d.split('.')[0]==a.device for d in available):
        result={'status':'unavailable','requested_device':a.device,'available_devices':available}
    else:
        engine=JointPolicy(a.device) if a.graph=='policy' else SafetyMonitor(a.device)
        if engine.compiled is None:raise RuntimeError('OpenVINO compilation failed; refusing to benchmark a NumPy fallback')
        rng=np.random.default_rng(23);errors=[]
        for i in range(a.samples+100):
            if a.graph=='policy':
                x=rng.uniform([.22,-.13,.025],[.405,.13,.17]).astype(np.float32)
                value=engine.predict(x);reference=features(x)@engine.weights
            else:
                x=rng.uniform(-1,1,(2,3)).astype(np.float32);value=engine.distance(x);reference=float(np.linalg.norm(x[0]-x[1]))
            errors.append(float(np.max(np.abs(value-reference))))
        times=(engine.times if a.graph=='policy' else engine.latencies)[100:]
        result={'status':'completed','device':a.device,'device_name':core.get_property(a.device,'FULL_DEVICE_NAME'),'available_devices':available,'openvino_version':ov.__version__,'platform':platform.platform(),'precision':'FP32 input and inference precision hint','graph':a.graph,'description':engine.engine,'warmup':100,'samples':a.samples,'latency_p50_ms':float(np.percentile(times,50)),'latency_p95_ms':float(np.percentile(times,95)),'serial_inferences_per_second':1000/float(np.mean(times)),'max_abs_reference_error':max(errors),'error_unit':'radians' if a.graph=='policy' else 'meters','limitations':'Host-specific graph microbenchmark. Learned policy output is a joint-target proposal with mandatory numerical correction. Does not measure end-to-end VLA or Intel Core Ultra performance unless device_name identifies that hardware.'}
    Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
