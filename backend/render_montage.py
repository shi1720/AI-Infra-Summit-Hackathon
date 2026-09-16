"""Ten seeded real physics rollouts, rendered into one audit montage."""
import tempfile
from pathlib import Path
import subprocess
import mujoco
import numpy as np
from PIL import Image,ImageDraw
from .so101 import SO101Simulation

def main():
    all_frames=[]
    with tempfile.TemporaryDirectory() as folder:
        for seed in range(10):
            sim=SO101Simulation(seed);run=sim.run('Set the table','grip_loss',True)
            images=[]
            with mujoco.Renderer(sim.model,height=240,width=320) as renderer:
                for frame in run['frames'][::5]:
                    sim.data.qpos[:]=frame['qpos'];mujoco.mj_forward(sim.model,sim.data);renderer.update_scene(sim.data,camera='overview')
                    im=Image.fromarray(renderer.render());draw=ImageDraw.Draw(im);draw.rectangle((0,0,320,38),fill='#101722');draw.text((8,4),f"Seed {seed} | {run['status']} | {frame['phase']}",fill='white',font_size=13);draw.text((8,21),f"{frame['time']:.2f}s | final cup error {run['metrics']['placement_error_mm']['cup']:.1f} mm",fill='#70e3c3',font_size=11);images.append(im)
            all_frames.append(images)
        n=max(map(len,all_frames))
        for i in range(n):
            canvas=Image.new('RGB',(1600,480),'#101722')
            for seed,frames in enumerate(all_frames):canvas.paste(frames[min(i,len(frames)-1)],((seed%5)*320,(seed//5)*240))
            canvas.save(Path(folder)/f'{i:05d}.png')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','4','-i',folder+'/%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart','backend/evidence/ten-seed-montage.mp4'],check=True)
    print('backend/evidence/ten-seed-montage.mp4')
if __name__=='__main__':main()
