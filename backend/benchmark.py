"""Benchmark the geometric graph on an explicitly selected OpenVINO device.

This does not benchmark a learned robotics policy or certify a deployment.
"""
import argparse,json,platform,time
from pathlib import Path
import numpy as np
import openvino as ov
from .simulation import SafetyMonitor

def main():
    p=argparse.ArgumentParser();p.add_argument('--device',choices=['CPU','GPU','NPU'],default='CPU');p.add_argument('--samples',type=int,default=1000);p.add_argument('--output',default='backend/evidence/device-benchmark.json');a=p.parse_args()
    core=ov.Core();available=core.available_devices
    if not any(d.split('.')[0]==a.device for d in available):
        result={'status':'unavailable','requested_device':a.device,'available_devices':available}
    else:
        monitor=SafetyMonitor(a.device)
        if monitor.compiled is None:raise RuntimeError('OpenVINO compilation failed; refusing to benchmark a NumPy fallback')
        rng=np.random.default_rng(23);errors=[]
        for i in range(a.samples+100):
            x=rng.uniform(-1,1,(2,3)).astype(np.float32);value=monitor.distance(x);errors.append(abs(value-float(np.linalg.norm(x[0]-x[1]))))
        times=monitor.latencies[100:]
        result={'status':'completed','device':a.device,'device_name':core.get_property(a.device,'FULL_DEVICE_NAME'),'available_devices':available,'openvino_version':ov.__version__,'platform':platform.platform(),'precision':'FP32 input and inference precision hint','graph':'Euclidean gripper separation, geometric operations, not trained ML','warmup':100,'samples':a.samples,'latency_p50_ms':float(np.percentile(times,50)),'latency_p95_ms':float(np.percentile(times,95)),'serial_inferences_per_second':1000/float(np.mean(times)),'max_abs_error_m':max(errors),'limitations':'Host-specific microbenchmark. Does not measure end-to-end policy or Intel Core Ultra hardware unless device_name identifies that hardware.'}
    Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
