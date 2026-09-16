from pathlib import Path
from .so101 import SO101Simulation
if __name__=='__main__':
 s=SO101Simulation();Path('backend/evidence/workcell.png').write_bytes(s.render_png())
 print('Rendered actual MuJoCo SO101 camera')
