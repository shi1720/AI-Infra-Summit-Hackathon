#!/usr/bin/env bash
# Reproducible hardware validation. No sudo, no API key, no cloud credentials.
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_ROOT"
GRANTED_OUT="${GRANTED_OUTPUT_DIR:-$TASK_ROOT/artifacts/intel-validation-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$GRANTED_OUT"
exec > >(tee "$GRANTED_OUT/run.log") 2>&1
printf 'Granted hardware validation started %s\n' "$(date -u +%FT%TZ)"
printf 'Outputs: %s\n' "$GRANTED_OUT"
GRANTED_PY=''
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3,11))' 2>/dev/null; then
    GRANTED_PY="$(command -v "$candidate")"
    break
  fi
done
if [ -z "$GRANTED_PY" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv python install 3.11
    GRANTED_PY="$(uv python find 3.11)"
  else
    printf 'Python 3.11+ or uv is required. No system changes were made.\n' >&2
    exit 1
  fi
fi
GRANTED_ENV="$TASK_ROOT/.venv-intel-validation"
if command -v uv >/dev/null 2>&1; then
  if [ ! -x "$GRANTED_ENV/bin/python" ]; then uv venv --seed --python "$GRANTED_PY" "$GRANTED_ENV"; fi
  uv pip install --python "$GRANTED_ENV/bin/python" -r backend/requirements.txt
else
  "$GRANTED_PY" -m venv "$GRANTED_ENV"
  "$GRANTED_ENV/bin/python" -m pip install -r backend/requirements.txt
fi
GRANTED_RUNPY="$GRANTED_ENV/bin/python"
export MUJOCO_GL="${MUJOCO_GL:-egl}"
"$GRANTED_RUNPY" - "$GRANTED_OUT/hardware.json" <<'PY'
import json,platform,subprocess,sys
from pathlib import Path
import openvino as ov
core=ov.Core()
report={'platform':platform.platform(),'architecture':platform.machine(),'python':sys.version,'openvino':ov.__version__,'devices':{d:core.get_property(d,'FULL_DEVICE_NAME') for d in core.available_devices}}
try:report['git_revision']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception:report['git_revision']='unavailable'
report['note']='Use the exact device name. Intel Xeon evidence is not Intel Core Ultra evidence; unavailable NPU or GPU is not a pass.'
Path(sys.argv[1]).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
PY
if command -v lscpu >/dev/null 2>&1; then lscpu --json > "$GRANTED_OUT/lscpu.json"; fi
"$GRANTED_RUNPY" -m pip freeze > "$GRANTED_OUT/dependencies.txt"
"$GRANTED_RUNPY" -m pytest tests/test_backend.py -q | tee "$GRANTED_OUT/tests.txt"
for GRANTED_DEVICE in CPU GPU NPU; do
  for GRANTED_GRAPH in policy monitor; do
    GRANTED_RESULT="$GRANTED_OUT/benchmark-${GRANTED_DEVICE}-${GRANTED_GRAPH}.json"
    if ! "$GRANTED_RUNPY" -m backend.benchmark --device "$GRANTED_DEVICE" --graph "$GRANTED_GRAPH" --output "$GRANTED_RESULT"; then
      printf '{"status":"failed","device":"%s","graph":"%s","detail":"Compilation or benchmark failed. See run.log. No fallback result claimed."}\n' "$GRANTED_DEVICE" "$GRANTED_GRAPH" > "$GRANTED_RESULT"
    fi
  done
done
# 50 randomized seeds x five conditions = 250 real physics rollouts.
"$GRANTED_RUNPY" -m backend.evaluate --seeds "${GRANTED_SEEDS:-50}" --output "$GRANTED_OUT/robustness.json"
"$GRANTED_RUNPY" -m backend.evaluate_policy --output "$GRANTED_OUT/policy-ablation.json"
cp backend/assets/joint_policy/training-report.json "$GRANTED_OUT/training-report.json"
cp backend/assets/joint_policy/MODEL_CARD.md "$GRANTED_OUT/MODEL_CARD.md"
if command -v ffmpeg >/dev/null 2>&1; then
  if "$GRANTED_RUNPY" -m backend.render_montage --output "$GRANTED_OUT/ten-seed-montage.mp4"; then
    printf '{"status":"completed","renderer":"MuJoCo","seeds":10}\n' > "$GRANTED_OUT/render-status.json"
  else
    printf '{"status":"failed","detail":"Graphics context unavailable or render failed. Physics and benchmark reports remain valid. See run.log."}\n' > "$GRANTED_OUT/render-status.json"
  fi
else
  printf '{"status":"unavailable","detail":"FFmpeg absent. Install it in user space or render the recorded results on another host."}\n' > "$GRANTED_OUT/render-status.json"
fi
# A missing GPU/NPU, graphics context, or non-Intel host is reported, never hidden.
GRANTED_ARCHIVE="$GRANTED_OUT.tar.gz"
tar -czf "$GRANTED_ARCHIVE" -C "$(dirname "$GRANTED_OUT")" "$(basename "$GRANTED_OUT")"
printf '\nValidation finished. Download: %s\n' "$GRANTED_ARCHIVE"
