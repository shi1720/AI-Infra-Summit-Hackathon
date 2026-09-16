"""Dual SO101 model adapted at runtime from MuJoCo Menagerie (Apache-2.0).

Changes: two prefixed copies, table and objects, grasp welds, contact masks.
Original upstream MJCF and meshes are retained unmodified in assets/so101.
"""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
import time
import numpy as np
import mujoco
from .simulation import Simulation, SafetyMonitor, STARTS

ROOT=Path(__file__).parent/'assets'/'so101'
BASES={'left':[-.28,-.25,.005],'right':[-.28,.25,.005]}

def dual_model():
    source=ET.parse(ROOT/'so101.xml').getroot()
    root=ET.Element('mujoco',model='Granted dual SO101 workcell')
    ET.SubElement(root,'compiler',angle='radian',meshdir=str(ROOT/'assets'),autolimits='true')
    ET.SubElement(root,'option',timestep='.002',gravity='0 0 -9.81',integrator='implicitfast')
    visual=ET.SubElement(root,'visual');ET.SubElement(visual,'global',offwidth='960',offheight='720')
    root.append(deepcopy(source.find('default')))
    root.append(deepcopy(source.find('asset')))
    world=ET.SubElement(root,'worldbody')
    ET.SubElement(world,'light',pos='0 0 1.5',dir='0 0 -1')
    ET.SubElement(world,'camera',name='overview',pos='.65 -.8 .75',xyaxes='.77 .64 0 -.34 .41 .84')
    ET.SubElement(world,'geom',name='table',type='plane',size='1 1 .1',rgba='.09 .12 .17 1',contype='1',conaffinity='1')
    acts=ET.SubElement(root,'actuator'); eqs=ET.SubElement(root,'equality')
    for side,base in BASES.items():
        body=deepcopy(source.find('worldbody/body'))
        for element in body.iter():
            if 'name' in element.attrib:element.set('name',side+'_'+element.get('name'))
            # Isolate the scripted grasp abstraction from mesh-finger contacts.
            # Table/object dynamics remain active. No full-body collision certification.
            if element.tag=='geom':element.set('contype','0');element.set('conaffinity','0')
        body.set('pos',' '.join(map(str,base)))
        body.find(".//site[@name='"+side+"_gripperframe']").set('name',side+'_tip')
        world.append(body)
        for actuator in source.find('actuator'):
            a=deepcopy(actuator)
            for key in ['name','joint']:a.set(key,side+'_'+a.get(key))
            acts.append(a)
        ET.SubElement(eqs,'weld',name=side+'_grasp',body1=side+'_gripper',body2='cup' if side=='left' else 'bowl',active='false',solref='.005 1')
    for name,p in STARTS.items():
        body=ET.SubElement(world,'body',name=name,pos=' '.join(map(str,p)))
        ET.SubElement(body,'freejoint',name=name+'_free')
        ET.SubElement(body,'geom',type='cylinder',size='.025 .025',mass='.035',rgba='1 .6 .2 1' if name=='cup' else '.4 .6 1 1',contype='1',conaffinity='1')
    return mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'))

class SO101Simulation(Simulation):
    def __init__(self,seed=42):
        self.model=dual_model();self.data=mujoco.MjData(self.model)
        self.monitor=SafetyMonitor();self.events=[];self.frames=[]
        self.min_separation=float('inf');self.seed=seed;self.rng=np.random.default_rng(seed)
        self.phase='observe';self.steps=0
        self.perturbations={}
        for name in STARTS:
            j=self.model.joint(name+'_free').qposadr[0]
            delta=self.rng.uniform(-.008,.008,2)
            self.data.qpos[j:j+2]+=delta
            body=self.model.body(name).id
            factor=float(self.rng.uniform(.8,1.2))
            self.model.body_mass[body]*=factor
            geom=self.model.body_geomadr[body]
            friction=float(self.rng.uniform(.8,1.2))
            self.model.geom_friction[geom,0]*=friction
            self.perturbations[name]={'xy_delta_mm':(delta*1000).round(3).tolist(),'mass_factor':round(factor,3),'friction_factor':round(friction,3)}
        self.robot='Dual SO101 (MuJoCo Menagerie)'
        for side in BASES:
            q=self.solve_ik(side,[*STARTS['cup' if side=='left' else 'bowl'][:2],.15])
            offset=0 if side=='left' else 6
            self.data.qpos[offset:offset+5]=q
            self.data.ctrl[offset:offset+5]=q
            self.data.qpos[offset+5]=.6;self.data.ctrl[offset+5]=.6
        mujoco.mj_forward(self.model,self.data)
    def solve_ik(self,side,point):
        offset=0 if side=='left' else 6
        temp=mujoco.MjData(self.model);temp.qpos[:]=self.data.qpos
        site=self.model.site(side+'_tip').id
        dofs=np.arange(offset,offset+5)
        limits=self.model.jnt_range[dofs]
        best=(1e9,None)
        # Damped least-squares pose IK: xyz plus a vertical gripper axis.
        for restart in range(5):
            if restart:temp.qpos[dofs]=self.rng.uniform(limits[:,0]*.7,limits[:,1]*.7)
            for _ in range(180):
                mujoco.mj_forward(self.model,temp)
                delta=np.asarray(point)-temp.site_xpos[site]
                body=self.model.body(side+'_gripper').id
                axis=temp.xmat[body].reshape(3,3)[:,2]
                rot=np.cross(axis,np.array([0.,0.,1.]))
                err=np.concatenate([delta,rot*.015])
                norm=np.linalg.norm(delta)+np.linalg.norm(rot)*.01
                if norm<best[0]:best=(norm,temp.qpos[dofs].copy())
                if np.linalg.norm(delta)<.001:return temp.qpos[dofs].copy()
                jp=np.zeros((3,self.model.nv));jr=np.zeros_like(jp)
                mujoco.mj_jacSite(self.model,temp,jp,jr,site)
                jac=np.vstack([jp[:,dofs],jr[:,dofs]*.015])
                dq=jac.T@np.linalg.solve(jac@jac.T+np.eye(6)*.0002,err)
                temp.qpos[dofs]=np.clip(temp.qpos[dofs]+np.clip(dq,-.12,.12),limits[:,0]+.005,limits[:,1]-.005)
        if best[0]>.025:raise ValueError(f'SO101 target unreachable: {best[0]:.3f} m weighted pose error')
        return best[1]
    def move(self,points,duration=1.4,phase='move'):
        self.phase=phase;start=self.data.ctrl.copy();target=start.copy()
        for side,p in points.items():
            offset=0 if side=='left' else 6
            target[offset:offset+5]=self.solve_ik(side,p)
        n=int(duration/self.model.opt.timestep)
        for i in range(n):
            t=(i+1)/n;self.data.ctrl[:]=start+(target-start)*(t*t*(3-2*t));self.step()
        for _ in range(150):self.step()
    def snapshot(self):
        self.frames.append({'time':round(float(self.data.time),3),'phase':self.phase,'qpos':self.data.qpos.round(6).tolist(),'left':{'joints':self.data.qpos[:6].round(5).tolist(),'tip':self.tip('left').round(5).tolist()},'right':{'joints':self.data.qpos[6:12].round(5).tolist(),'tip':self.tip('right').round(5).tolist()},'objects':[{'name':n,'x':round(float(self.object_pos(n)[0]),5),'y':round(float(self.object_pos(n)[1]),5),'z':round(float(self.object_pos(n)[2]),5)} for n in STARTS]})
    def render_png(self):
        from PIL import Image
        import io
        with mujoco.Renderer(self.model,height=480,width=640) as renderer:
            renderer.update_scene(self.data,camera='overview')
            pixels=renderer.render()
        output=io.BytesIO();Image.fromarray(pixels).save(output,format='PNG')
        return output.getvalue()
    def run(self,*args,**kwargs):
        result=super().run(*args,**kwargs)
        result['robot']=self.robot
        result['perturbations']=self.perturbations
        result['limitations']=['SO101 kinematics and inertias from MuJoCo Menagerie, not real hardware','Ground-truth object poses, not camera perception','Grasping uses weld constraints, not contact-based finger control','Arm mesh contacts disabled; gripper separation gate is not full-body collision checking','OpenVINO executes a geometric graph, not a trained VLA policy','Simulation results do not certify physical robot safety']
        return result
