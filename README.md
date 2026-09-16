# Granted Robotics

**A robot's plan will break. The recovery should be inspectable.**

Granted Robotics is a simulation workbench for bimanual table setting, action checks, and fault recovery. Created by **Shivam Gupta** for the AI Infra Summit Hackathon with AI-assisted development.

- [Open the workbench](https://granted-robotics.web.app)
- [Project story](deliverables/project-story.md)
- [Pitch deck](deliverables/granted-robotics-pitch.pdf)
- [Demo script](deliverables/video-script.md)

## Why it exists

A moved cup or a failed grasp can invalidate an otherwise reasonable plan. Robotics integrators need to reproduce that failure, inspect the intervention, and establish what the resulting execution actually achieved. Granted explores a lightweight workflow for that job.

## What is implemented

The React and TypeScript workbench explains planning, approval, intervention, and recovery. The Python service executes a separate MuJoCo fixture with two SO101 arms from MuJoCo Menagerie and two tabletop objects. It uses inverse kinematics and position control, free-body objects, and simulated grasp weld constraints. An OpenVINO CPU graph computes geometric safety signals.

Fault scenarios include a displaced object, grip loss, and a workspace obstacle. The backend exports events, sampled states, placement errors, physics step counts, and monitor latency. Structured language planning can optionally use OpenAI through a server-side environment variable. Without a key, the backend clearly labels its deterministic planner.

**Scope:** this is a simulation MVP. The controller is deterministic, not a trained VLA policy. The safety graph is geometric, not a learned safety model. Nothing here certifies a physical robot. The browser visualization illustrates workflow and must not be confused with a live physics renderer. Refer to the explicitly labeled backend evidence for MuJoCo measurements.

## Track compliance

The full Intel online brief additionally requires camera-based multimodal reasoning, policy training or fine-tuning, a ten-seed demonstration, and final execution on Intel Core Ultra Series 2/3. This prototype does not claim full track compliance. We have not demonstrated it on Intel Core Ultra hardware or trained a VLA policy. See [track readiness](deliverables/track-readiness.md) for the precise gaps.

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

The fixture randomizes each object's initial XY position by +/-8 mm and scales mass and sliding friction from 0.8x to 1.2x. Mean cup error for grip-loss recovery is 14.76 mm, compared with 159.82 mm without recovery. These controlled fixture results do not establish broad generalization to new tasks, lighting, shapes, or hardware.

The FP32 OpenVINO geometric graph benchmark reports p50 0.02367 ms and p95 0.03050 ms across 1,000 samples after 100 warmups. This was measured on an Apple arm64 development machine. It is **not an Intel Core Ultra benchmark** and does not measure VLA inference. See `backend/evidence/evaluation.json` for full configuration and records. `backend/evidence/so101-recovery.mp4` shows actual MuJoCo rendering.


## Architecture

```text
Web workbench (React + TypeScript)
    |
    | optional simulation API
    v
FastAPI request validation and bounded workers
    |
    +-- Structured task planner (deterministic or optional OpenAI)
    +-- MuJoCo physics and deterministic controller
    +-- OpenVINO geometric safety graph
    +-- Events, sampled states, metrics, exported evidence
```

## Commercial hypothesis

The proposed customer is a robotics integrator with recurring deployment failures. The initial paid pilot would import one task and measure time spent diagnosing regressions. A $500 monthly team workspace is a pricing experiment, not validated demand. See [the business case](deliverables/business-case.md) for assumptions and limitations.

## Before production use

A commercial deployment needs durable storage, real identity and access control, tenant isolation, workload quotas, operational monitoring, and hardware-specific safety validation. A local demo session is not production authentication. The current in-memory API is designed for demonstration, not long-term customer data retention.

## Submission assets

`deliverables/` contains the project story, pitch PDF and editable PPTX, cover image, narrated video with burnt captions, caption SRT, verbatim script, and YouTube metadata. Files under `.build/` are generation intermediates and should not be published as source assets.

## License

MIT. See [LICENSE](LICENSE). Third-party packages retain their respective licenses.
