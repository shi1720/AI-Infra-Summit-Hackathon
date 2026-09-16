from .so101 import SO101Simulation
import json
if __name__=='__main__':
    for fault in ['none','grip_loss','object_displaced']:
        s=SO101Simulation()
        r=s.run('Set the table',fault)
        print(fault,r['status'],r['metrics'])
        print(r['events'])
