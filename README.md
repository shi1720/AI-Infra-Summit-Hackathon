# Granted Robotics

**A robot's plan will break. The recovery should be inspectable.**

Granted Robotics is a simulation workbench for bimanual table setting, action checks, and fault recovery. Created by **Shivam Gupta** for the AI Infra Summit Hackathon with AI-assisted development.

- [Open the workbench](https://granted-robotics.web.app)
- [Watch the complete demo](https://youtu.be/mSRJfgEWN08)
- [Submitted project](https://lablab.ai/ai-hackathons/ai-infra-summit-hackathon/granted-robotics/granted-robotics-permission-before-motion)
- [Project story](deliverables/project-story.md)
- [Pitch deck](deliverables/granted-robotics-complete-presentation.pdf)
- [Demo script](deliverables/complete-video-script.md)

## Why it exists

A moved cup or a failed grasp can invalidate an otherwise reasonable plan. Robotics integrators need to reproduce that failure, inspect the intervention, and establish what the resulting execution actually achieved. Granted explores a lightweight workflow for that job.

## What is implemented

The React and TypeScript workbench explains planning, approval, intervention, and recovery. The Python service executes a separate MuJoCo fixture with two SO101 arms from MuJoCo Menagerie and two tabletop objects. It uses inverse kinematics and position control, free-body objects, and simulated grasp weld constraints. An OpenVINO CPU graph computes geometric safety signals.

Fault scenarios include a displaced object, grip loss, and a workspace obstacle. The backend exports events, sampled states, placement errors, physics step counts, and monitor latency. Camera and language validation can optionally use OpenAI through a server-side environment variable. A raw MuJoCo camera image accompanies the task and the output must pass a strict schema. Without a key, the backend clearly labels its deterministic planner.

**Scope:** this is a simulation MVP. The controller uses a small learned joint-target proposal model followed by mandatory numerical correction. This is not an end-to-end VLA policy. The safety graph is geometric, not a learned safety model. Nothing here certifies a physical robot. The browser visualization illustrates workflow and must not be confused with a live physics renderer. Refer to the explicitly labeled backend evidence for MuJoCo measurements.

## Track compliance

The full Intel online brief additionally requires camera-based multimodal reasoning, policy training or fine-tuning, a ten-seed demonstration, and final execution on Intel Core Ultra Series 2/3. This prototype does not claim full track compliance. We have not demonstrated it on Intel Core Ultra hardware or trained an end-to-end VLA policy. See [track readiness](deliverables/track-readiness.md) for the precise gaps.

## Run the web app

Requires Node.js 20 or later.

```sh
npm install
npm run dev
```

For a production build:

```sh
npm run build
npm run preview
```

## Run the physics backend

Python 3.11 or later is recommended. OpenVINO wheel availability depends on your platform.

```sh
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.cli --fault grip_loss --output artifacts/grip-loss.json
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

The API documentation is available at `http://127.0.0.1:8000/docs`. The service exposes `GET /api/health`, `POST /api/runs`, and `GET /api/runs/{run_id}`. It keeps the last 30 runs in process memory. Export evidence to retain it.

Example request:

```sh
curl -X POST http://127.0.0.1:8000/api/runs \
  -H 'Content-Type: application/json' \
  -d '{"instruction":"Set the table with a cup and bowl","fault":"grip_loss","seed":42,"recovery":true}'
```

To compare recovery with the same fault and seed:

```sh
python -m backend.cli --fault grip_loss --seed 42 --output artifacts/recovered.json
python -m backend.cli --fault grip_loss --seed 42 --no-recovery --output artifacts/unrecovered.json
```

Optional server settings: `OPENAI_API_KEY` enables constrained language planning, and `CORS_ORIGINS` is a comma-separated list of allowed frontend origins. Keep API keys on the server. Do not add keys to source code or browser builds.

## Evaluation and runtime benchmark

```sh
python -m backend.evaluate --seeds 10 --output artifacts/evaluation.json
python -m backend.benchmark --device CPU --samples 1000 --output artifacts/cpu-benchmark.json
python -m pytest tests/test_backend.py -q
```

On an Intel system, the benchmark also accepts `--device GPU` or `--device NPU`. It reports unavailable devices rather than inventing results. The graph benchmark is separate from policy evaluation.

## Recorded evidence

The files in `backend/evidence/` are actual local MuJoCo executions. The final evaluation runs 10 seeds across five conditions, for 50 runs total:

| Condition | Task completed | Safely blocked |
| --- | ---: | ---: |
| Nominal | 10/10 | 0/10 |
| Object displaced, recovery on | 10/10 | 0/10 |
| Grip loss, recovery on | 10/10 | 0/10 |
| Grip loss, recovery off | 0/10 | 0/10 |
| Workspace obstacle | 0/10 | 10/10 |

The fixture randomizes each object's initial XY position by +/-8 mm and scales mass and sliding friction from 0.8x to 1.2x, varies cylinder radius and height by +/-8%, and varies lighting and table color. Mean cup error for grip-loss recovery is 14.05 mm, compared with 160.96 mm without recovery. These controlled fixture results do not establish broad generalization to new tasks, novel objects, or hardware.

The FP32 OpenVINO geometric graph benchmark reports p50 0.02433 ms and p95 0.03001 ms across 1,000 samples after 100 warmups. This was measured on an Apple arm64 development machine. It is **not an Intel Core Ultra benchmark** and does not measure VLA inference. See `backend/evidence/evaluation.json` for full configuration and records. `backend/evidence/so101-recovery.mp4` shows actual MuJoCo rendering.


## Learned policy and paired evaluation

A degree-4 polynomial model learns joint-target proposals from 600 SO101 inverse-kinematics demonstrations, split into 480 training and 120 held-out examples. Held-out joint RMSE is 0.19644 radians and MAE is 0.05373 radians. The model exports to OpenVINO FP32 IR. Its output initializes mandatory numerical pose correction rather than replacing it.

Across ten paired grip-loss seeds, both the baseline and learned-plus-correction controller completed 10/10 trials. Mean numerical IK iterations fell from 4,528.1 to 4,288.2, about 5.3%. Local mean simulation compute time changed from 271.05 ms to 255.76 ms. These timings include workload and host variation and do not establish Intel performance. The learned policy's local OpenVINO median inference was 0.03750 ms across 1,000 samples after 100 warmups. See `backend/evidence/policy-evaluation.json` and `backend/assets/joint_policy/training-report.json`.

This state-based imitation model does not learn vision or language. The camera-aware language validator is a separate component. Neither the joint prediction error nor the small fixture evaluation establishes unassisted learned manipulation.

## Architecture

```text
Web workbench (React + TypeScript)
    |
    | optional simulation API
    v
FastAPI request validation and bounded workers
    |
    +-- Structured task planner (deterministic or optional OpenAI)
    +-- MuJoCo physics, learned proposals and numerical correction
    +-- OpenVINO geometric safety graph
    +-- Events, sampled states, metrics, exported evidence
```

## Commercial hypothesis

The proposed customer is a robotics integrator with recurring deployment failures. The initial paid pilot would import one task and measure time spent diagnosing regressions. A $500 monthly team workspace is a pricing experiment, not validated demand. See [the business case](deliverables/business-case.md) for assumptions and limitations.

## Before production use

A commercial deployment needs durable storage, tenant authorization and isolation, workload quotas, operational monitoring, and hardware-specific safety validation. Firebase Authentication provides sign-in. Run history remains browser-local, and sign-in does not provide cross-device synchronization. The current in-memory API is designed for demonstration, not long-term customer data retention.

## Submission assets

`deliverables/` contains the project story, pitch PDF and editable PPTX, cover image, narrated video with burnt captions, caption SRT, verbatim script, and YouTube metadata. Files under `.build/` are generation intermediates and should not be published as source assets.

## License

MIT. See [LICENSE](LICENSE). Third-party packages and robot assets retain their respective licenses. See the license files shipped with the MuJoCo Menagerie assets.
