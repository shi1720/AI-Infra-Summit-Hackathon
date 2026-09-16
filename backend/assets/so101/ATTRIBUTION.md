# SO101 model attribution

Original model and meshes: MuJoCo Menagerie, `robotstudio_so101`.
Source: https://github.com/google-deepmind/mujoco_menagerie/tree/8161bba264d7fa7c99ca301e91e7fb44737676ad/robotstudio_so101
Downloaded commit: `8161bba264d7fa7c99ca301e91e7fb44737676ad`.
Upstream robot: The Robot Studio SO101, with model derivation by I2RT Robotics.
License: Apache License 2.0, retained in `LICENSE`.

The original `so101.xml` and mesh assets are unmodified. Granted's
`backend/so101.py` constructs an adapted scene at runtime: two named copies,
base placement, a table, colored tableware proxies, object dynamics, camera,
and equality constraints for simulated grasps. Mesh contacts are disabled in
this adapted workcell. This is not a full collision model or a real robot
controller. The original model authors do not endorse this project.
