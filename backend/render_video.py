"""Render the recorded SO101 physics states, not an illustrative animation."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import mujoco
import numpy as np
from PIL import Image, ImageDraw
from .so101 import SO101Simulation

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fault',default='grip_loss');parser.add_argument('--output',default='backend/evidence/so101-recovery.mp4');args=parser.parse_args()
    sim=SO101Simulation(42);result=sim.run('Set the table with a cup and bowl',args.fault)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(result,indent=2))
    with tempfile.TemporaryDirectory() as folder:
        with mujoco.Renderer(sim.model,height=720,width=960) as renderer:
            for i,frame in enumerate(result['frames']):
                sim.data.qpos[:]=frame['qpos'];mujoco.mj_forward(sim.model,sim.data)
                renderer.update_scene(sim.data,camera='overview');im=Image.fromarray(renderer.render())
                draw=ImageDraw.Draw(im);draw.rectangle((0,0,960,72),fill='#101722');draw.text((24,16),'GRANTED  |  Actual MuJoCo dual SO101 rollout',fill='white',font_size=23);draw.text((24,45),f"{frame['phase'].upper()}   {frame['time']:.2f}s   Fault: {args.fault}",fill='#70e3c3',font_size=18)
                latest=[e for e in result['events'] if e['time']<=frame['time']]
                if latest:
                    message=latest[-1]['message'];draw.rectangle((0,660,960,720),fill='#101722');draw.text((20,680),message[:98],fill='white',font_size=16)
                im.save(Path(folder)/f'{i:05d}.png')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','20','-i',folder+'/%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
    print(str(out))
if __name__=='__main__':main()
