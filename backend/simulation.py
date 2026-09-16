"""Two articulated 3-DOF arms with measured MuJoCo state and grasp constraints.

The gripper uses an equality weld, a common simulation abstraction. This is not
SO-101 hardware, a learned VLA, or evidence of real-world manipulation success.
"""
from __future__ import annotations
import math
import time
import uuid
import numpy as np
import mujoco

OBJECTS = ['cup', 'bowl']
BASES = {'left': [-.28, -.25, .20], 'right': [-.28, .25, .20]}
STARTS = {'cup': [-.05, -.16, .025], 'bowl': [-.05, .16, .025]}
TARGETS = {'cup': [.12, -.16, .025], 'bowl': [.12, .16, .025]}

def scene_xml():
    arms, actuators, equalities = [], [], []
    for side, base in BASES.items():
        color = '.20 .77 .66 1' if side == 'left' else '.45 .55 .95 1'
        arms.append(f'''<body name="{side}_base" pos="{' '.join(map(str,base))}">
          <geom type="cylinder" size=".045 .025" rgba="{color}"/>
          <body name="{side}_yaw"><inertial pos="0 0 0" mass=".05" diaginertia=".0001 .0001 .0001"/><joint name="{side}_yaw" axis="0 0 1" range="-180 180"/>
          <body name="{side}_upper"><joint name="{side}_shoulder" axis="0 1 0" range="-150 150"/>
          <geom type="capsule" fromto="0 0 0 .25 0 0" size=".014" rgba="{color}"/>
          <body name="{side}_forearm" pos=".25 0 0"><joint name="{side}_elbow" axis="0 1 0" range="-160 160"/>
          <geom type="capsule" fromto="0 0 0 .25 0 0" size=".012" rgba="{color}"/>
          <body name="{side}_gripper" pos=".25 0 0"><geom type="sphere" size=".016" rgba="{color}"/><site name="{side}_tip" size=".006"/></body>
          </body></body></body></body>''')
        for joint in ['yaw', 'shoulder', 'elbow']:
            actuators.append(f'<position joint="{side}_{joint}" kp="160" kv="18" forcerange="-60 60"/>')
        obj = 'cup' if side == 'left' else 'bowl'
        equalities.append(f'<weld name="{side}_grasp" body1="{side}_gripper" body2="{obj}" active="false" solref=".005 1"/>')
    objects = ''.join(f'<body name="{name}" pos="{" ".join(map(str,pos))}"><freejoint name="{name}_free"/><geom type="cylinder" size=".025 .025" mass=".05" rgba="{(".99 .62 .28 1" if name == "cup" else ".50 .65 1 1")}" contype="1" conaffinity="1"/></body>' for name,pos in STARTS.items())
    return f'''<mujoco model="Granted dual arm workbench"><compiler angle="degree"/><option timestep=".002" gravity="0 0 -9.81" integrator="implicitfast"/><default><joint damping="2" armature=".01"/><geom contype="0" conaffinity="0" density="500"/></default><worldbody><light pos="0 0 2"/><geom name="table" type="plane" size="1 1 .1" rgba=".10 .14 .20 1" contype="1" conaffinity="1"/>{''.join(arms)}{objects}</worldbody><actuator>{''.join(actuators)}</actuator><equality>{''.join(equalities)}</equality></mujoco>'''

class SafetyMonitor:
    """OpenVINO compiled geometric separation graph, not a learned model."""
    def __init__(self, device='CPU'):
        self.engine = 'NumPy geometric monitor'
        self.compiled = None
        self.latencies = []
        try:
            import openvino as ov
            from openvino import opset13 as op
            x = op.parameter([2, 3], np.float32, name='gripper_positions')
            a = op.gather(x, op.constant(0), op.constant(0))
            b = op.gather(x, op.constant(1), op.constant(0))
            delta = op.subtract(a,b)
            distance = op.sqrt(op.reduce_sum(op.multiply(delta,delta), op.constant([0]), False))
            self.compiled = ov.Core().compile_model(ov.Model([distance], [x], 'gripper_separation'), device, {'INFERENCE_PRECISION_HINT':'f32'})
            self.engine = 'OpenVINO '+device+' geometric safety graph'
        except (ImportError, RuntimeError, TypeError):
            pass
    def distance(self, positions):
        start = time.perf_counter()
        x = np.asarray(positions, dtype=np.float32)
        result = float(self.compiled([x])[0].item()) if self.compiled else float(np.linalg.norm(x[0]-x[1]))
        self.latencies.append((time.perf_counter()-start)*1000)
        return result

def ik(side, point):
    dx, dy, dz = np.asarray(point)-np.asarray(BASES[side])
    radius = math.hypot(dx,dy)
    c = (radius*radius+dz*dz-.125)/.125
    if not -1.00001 <= c <= 1.00001:
        raise ValueError('Target exceeds the 0.5 m arm workspace')
    elbow = math.acos(max(-1,min(1,c)))
    shoulder = math.atan2(-dz,radius)-math.atan2(.25*math.sin(elbow),.25+.25*math.cos(elbow))
    return np.array([math.atan2(dy,dx),shoulder,elbow])

class Simulation:
    def __init__(self, seed=42):
        self.model = mujoco.MjModel.from_xml_string(scene_xml())
        self.data = mujoco.MjData(self.model)
        self.monitor = SafetyMonitor()
        self.events, self.frames = [], []
        self.min_separation = float('inf')
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.phase = 'observe'
        self.steps = 0
        for side in BASES:
            joints = ik(side, STARTS['cup' if side == 'left' else 'bowl'][:2]+[.15])
            offset = 0 if side == 'left' else 3
            self.data.qpos[offset:offset+3] = joints
            self.data.ctrl[offset:offset+3] = joints
        mujoco.mj_forward(self.model,self.data)
    def object_pos(self, name):
        return self.data.body(name).xpos.copy()
    def tip(self, side):
        return self.data.site(side+'_tip').xpos.copy()
    def event(self, kind, message, **extras):
        self.events.append({'time':round(float(self.data.time),3),'kind':kind,'message':message,**extras})
    def snapshot(self):
        self.frames.append({'time':round(float(self.data.time),3),'phase':self.phase,'left':{'joints':self.data.qpos[:3].round(5).tolist(),'tip':self.tip('left').round(5).tolist()},'right':{'joints':self.data.qpos[3:6].round(5).tolist(),'tip':self.tip('right').round(5).tolist()},'objects':[{'name':n,'x':round(float(self.object_pos(n)[0]),5),'y':round(float(self.object_pos(n)[1]),5),'z':round(float(self.object_pos(n)[2]),5)} for n in OBJECTS]})
    def step(self):
        mujoco.mj_step(self.model,self.data)
        self.steps += 1
        if self.steps % 25 == 0:
            separation=self.monitor.distance([self.tip('left'),self.tip('right')])
            self.min_separation=min(self.min_separation,separation)
            if separation < .08:
                raise RuntimeError('Gripper separation violated: simulation stopped')
            self.snapshot()
    def move(self, points, duration=1.4, phase='move'):
        self.phase=phase
        start=self.data.ctrl.copy()
        target=start.copy()
        for side,point in points.items():
            offset=0 if side=='left' else 3
            target[offset:offset+3]=ik(side,point)
        n=int(duration/self.model.opt.timestep)
        for i in range(n):
            t=(i+1)/n
            blend=t*t*(3-2*t)
            self.data.ctrl[:]=start+(target-start)*blend
            self.step()
        for _ in range(150): self.step()
    def settle(self, seconds=.5):
        for _ in range(int(seconds/self.model.opt.timestep)): self.step()
    def grasp(self, side, name):
        error=float(np.linalg.norm(self.tip(side)-self.object_pos(name)))
        if error>.035: raise RuntimeError(f'{side} grasp rejected: {error:.3f} m approach error')
        # Capture current relative pose so activating the constraint never teleports the object.
        b1=self.model.body(side+'_gripper').id
        b2=self.model.body(name).id
        eq=self.model.equality(side+'_grasp').id
        rot=self.data.xmat[b1].reshape(3,3)
        self.model.eq_data[eq,3:6]=rot.T@(self.data.xpos[b2]-self.data.xpos[b1])
        inv=np.empty(4); rel=np.empty(4)
        mujoco.mju_negQuat(inv,self.data.xquat[b1])
        mujoco.mju_mulQuat(rel,inv,self.data.xquat[b2])
        self.model.eq_data[eq,6:10]=rel
        self.data.eq_active[eq]=1
        self.event('grasp',f'{side.title()} gripper secured {name}', approach_error_mm=round(error*1000,2))
    def release(self,side):
        self.data.eq_active[self.model.equality(side+'_grasp').id]=0
    def displace(self,name,dx):
        q=self.model.joint(name+'_free').qposadr[0]
        self.data.qpos[q]+=dx
        mujoco.mj_forward(self.model,self.data)

    def run(self, instruction, fault='none', recovery=True):
        began=time.perf_counter()
        self.event('observe','Observed cup and bowl in their independent arm workspaces')
        status='completed'
        recoveries=0
        self.snapshot()
        if fault=='object_displaced':
            self.displace('cup',.065)
            self.event('fault','Cup displaced 65 mm after initial observation')
            if recovery:
                recoveries+=1; self.event('recovery','Re-observed cup pose and replanned the left approach')
        if fault=='obstacle':
            self.event('fault','Injected exclusion zone blocks the transport corridor')
            self.event('safety_stop','Request stopped before movement; operator must clear the exclusion zone')
            status='blocked'
        else:
            try:
                observed={s:self.object_pos('cup' if s=='left' else 'bowl') for s in BASES}
                if fault=='object_displaced' and not recovery: observed['left']=np.array(STARTS['cup'])
                self.move({s:[*p[:2],.12] for s,p in observed.items()},phase='approach')
                self.move(observed,phase='grasp')
                self.grasp('left','cup'); self.grasp('right','bowl')
                self.move({s:[*p[:2],.16] for s,p in observed.items()},phase='lift')
                if fault=='grip_loss':
                    self.release('left'); self.event('fault','Left grasp constraint released to simulate a dropped cup'); self.settle(.6)
                    if recovery:
                        recoveries+=1
                        self.event('recovery','Detected cup outside gripper tolerance; paused right arm and regrasped cup')
                        p=self.object_pos('cup')
                        self.move({'left':[*p[:2],.12]},phase='recover')
                        self.move({'left':p},phase='recover')
                        self.grasp('left','cup')
                        self.move({'left':[*p[:2],.16]},phase='lift')
                self.move({'left':[.12,-.16,.16],'right':[.12,.16,.16]},phase='transport')
                self.move({'left':TARGETS['cup'],'right':TARGETS['bowl']},phase='place')
                self.release('left'); self.release('right')
                self.settle(.5)
                self.move({'left':[.12,-.16,.16],'right':[.12,.16,.16]},phase='verify')
                self.settle(.5)
            except (RuntimeError,ValueError) as exc:
                status='failed';self.event('safety_stop',str(exc))
        errors={n:float(np.linalg.norm(self.object_pos(n)[:2]-np.array(TARGETS[n])[:2])) for n in OBJECTS}
        successes={n:bool(e<.035 and abs(self.object_pos(n)[2]-.025)<.025) for n,e in errors.items()}
        if status=='completed' and not all(successes.values()): status='failed'
        self.event('verification',f'{sum(successes.values())}/2 objects within 35 mm placement tolerance',errors_mm={n:round(e*1000,2) for n,e in errors.items()})
        self.snapshot()
        return {'id':str(uuid.uuid4()),'status':status,'instruction':instruction,'fault':fault,'seed':self.seed,'recovery_enabled':recovery,'engine':'MuJoCo '+mujoco.__version__,'safety_engine':self.monitor.engine,'planner':'deterministic structured task planner','summary':{'completed_objects':sum(successes.values()),'total_objects':2,'recoveries':recoveries,'message':('Both objects placed and verified' if status=='completed' else 'Safety gate blocked execution' if status=='blocked' else 'Placement verification failed')},'metrics':{'placement_error_mm':{n:round(e*1000,2) for n,e in errors.items()},'success':all(successes.values()),'simulated_seconds':round(float(self.data.time),3),'compute_ms':round((time.perf_counter()-began)*1000,2),'physics_steps':self.steps,'min_gripper_separation_mm':None if not math.isfinite(self.min_separation) else round(self.min_separation*1000,2),'monitor_median_ms':round(float(np.median(self.monitor.latencies)),4) if self.monitor.latencies else None,'recoveries':recoveries},'plan':[{'step':i+1,'action':a} for i,a in enumerate(['Observe object poses','Validate independent workspaces','Approach and secure both objects','Lift and transport','Place and release','Measure placement error'])],'events':self.events,'frames':self.frames,'limitations':['Custom 3-DOF arms, not SO-101 hardware','Ground-truth poses, not camera perception','Grasping uses weld constraints, not contact-based finger control','OpenVINO executes a geometric graph, not a trained VLA policy','Simulation results do not certify physical robot safety']}
