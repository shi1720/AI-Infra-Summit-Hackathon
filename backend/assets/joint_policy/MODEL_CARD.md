# SO101 joint-target imitation policy

This small supervised model learns a local mapping from a desired 3D gripper
position to five SO101 joint angles. It is a degree-four polynomial regressor,
trained by regularized least squares on numerical inverse-kinematics teacher
outputs. It is original project code and data, under the repository MIT license.

## Training and reproducibility

Run `python -m backend.train_policy --samples 600` from the repository root.
Sampling seed: 1720. Inputs: relative X and Y, world Z, in meters.
Domain: X 0.22 to 0.405, Y -0.13 to 0.13, Z 0.025 to 0.17.
The first 480 examples train the model and the remaining 120 are held out.
`demonstrations.npz` contains all teacher inputs and outputs plus the split index.
`weights.npy` contains the trained coefficients. `policy.xml` and `policy.bin`
are an OpenVINO FP32 export. `training-report.json` contains measured errors.

## Intended use

The model proposes joint targets to initialize damped least-squares IK. Numerical
pose correction, joint limits, gripper separation monitoring and final object
placement verification remain mandatory. If the model is absent, the service
uses numerical IK directly and labels that runtime.

This is not an end-to-end vision-language-action model. Camera-plus-language
validation uses a separate optional model; object poses come from simulation
state. The imitation model does not infer poses from images or understand text.

## Evaluation

Run `python -m backend.evaluate_policy`. The paired ten-seed grip-loss experiment
compares the learned proposal plus correction with IK alone. Both completed ten
of ten runs in this test. The learned proposal reduced mean solver iterations
from 4528.1 to 4288.2. This is a local observed result, not a universal acceleration
claim. Held-out joint RMSE was about 0.196 radians, which is too large to justify
unassisted deployment; the corrective controller is an essential component.

The published graph latency was measured on Apple M4 Pro through OpenVINO CPU.
Intel Core Ultra, GPU and NPU performance remain unverified. Use
`python -m backend.benchmark --device CPU --graph policy` or select GPU/NPU
on appropriate hardware. The tool reports unavailable devices honestly.

## Limitations

The sampled workspace is narrow. Teacher solutions can differ between IK
branches. There is no real robot training, real-world validation, hardware
safety guarantee, drawer manipulation, liquid pouring or learned perception.
