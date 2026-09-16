# Granted simulation service

Requires Python 3.11 or newer. No hardware or provider credential is needed for deterministic runs.

```sh
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
backend/.venv/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8080
```

Optional server environment: `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`),
`CORS_ORIGINS` (comma-separated), and `MAX_LLM_CALLS` (default 300 per process).
Never put provider keys in the web client. Public demonstration rate limit:
12 run requests per client address per minute, two concurrent simulation workers.
Cloud Run should use a small maximum instance count. This is a demo cost guard,
not a distributed production rate limiter.

## API

`GET /api/health` reports actual dependencies and configured language planner.
`POST /api/runs` accepts:

```json
{"instruction":"Set the table with a cup and bowl","fault":"grip_loss","seed":42,"recovery":true}
```

Faults: `none`, `object_displaced`, `grip_loss`, `obstacle`.
Response includes measured metrics, event times, state frames, randomization,
model provenance and limitations. `GET /api/runs/{id}` retrieves a recent trace.
Only the last 30 runs remain in process memory. Export the JSON for persistence.
Unsupported tasks return HTTP 422. Every accepted task is constrained to the
cup-and-bowl table-setting workcell. A configured language model receives an
actual rendered RGB image plus instruction. It approves the scene and fixed
task schema. MuJoCo ground-truth poses feed the numerical IK controller.

## Reproduce evidence

```sh
backend/.venv/bin/python -m pytest tests/test_backend.py -q
backend/.venv/bin/python -m backend.cli --fault grip_loss --output artifacts/run.json
backend/.venv/bin/python -m backend.cli --fault grip_loss --no-recovery --output artifacts/ablation.json
backend/.venv/bin/python -m backend.train_policy --samples 600
backend/.venv/bin/python -m backend.evaluate_policy
backend/.venv/bin/python -m backend.evaluate --seeds 10
backend/.venv/bin/python -m backend.benchmark --device CPU
backend/.venv/bin/python -m backend.benchmark --device NPU
backend/.venv/bin/python -m backend.render_video
backend/.venv/bin/python -m backend.render_montage
```

The render commands need FFmpeg and a working graphics context. Linux containers
use `MUJOCO_GL=egl`; the supplied Dockerfile includes EGL libraries. The NPU or
GPU benchmark records unavailability rather than substituting CPU results.

## Scope and limitations

- Real MuJoCo dynamics with two upstream SO101 models and seed variation in XY,
  mass and friction. Original model license and attribution are retained.
- Numerical damped least-squares IK drives the actual model position actuators.
- Weld constraints model grasps. Tableware uses simple colored cylinder proxies.
- Arm mesh contacts are disabled. The OpenVINO gripper-distance gate does not
  provide full-body collision avoidance or a physical robot safety guarantee.
- The obstacle test exercises a software exclusion-zone stop, not camera
  obstacle detection or simulated collision response.
- OpenVINO executes a trained polynomial joint-target imitation policy and a
  geometric FP32 separation graph. The learned proposal always undergoes numerical
  pose correction. It is not an end-to-end trained vision-language-action model.
  Training data, weights, OpenVINO IR, held-out errors and rollout ablations are included.
- Local benchmarks were measured on Apple M4 Pro. Intel Core Ultra performance
  is unverified. Cloud CPU execution is not equivalent to the required edge device.
- Tasks do not yet include drawers, tool retrieval, handoffs or liquid pouring.
- The local regression tests and seed evaluation do not call the paid language
  provider. Provider integration must be checked separately on the deployment.
