# Testing Granted Robotics

Application: https://granted-robotics.web.app
Repository: https://github.com/shi1720/AI-Infra-Summit-Hackathon

## Browser walkthrough

1. Open the app in a recent desktop or mobile browser.
2. Choose the Serve with confidence preset and a disturbance scenario.
3. Generate the plan, review its steps, and approve execution.
4. For a recovery scenario, inspect the safety hold and approve recovery.
5. Inspect the resulting event trail and export JSON evidence.
6. Open the backend evidence view if available. Recorded evidence is labeled separately from browser workflow animation.

The browser walkthrough illustrates the interaction flow. It does not establish that a physical robot ran or that its animation is a MuJoCo rendering.

## Reproduce physics evidence

Follow the Python setup in the README, then run:

```sh
python -m backend.cli --fault grip_loss --seed 42 --output artifacts/recovered.json
python -m backend.cli --fault grip_loss --seed 42 --no-recovery --output artifacts/unrecovered.json
```

Inspect `summary.completed_objects`, `metrics.success`, `metrics.placement_error_mm`, and the event history. Recovery should complete both fixture objects in the recorded seed-42 case. Compare with the unrecovered case rather than inferring recovery performance from the UI alone.

The OpenVINO engine name in the result confirms whether that runtime handled safety evaluation. Timing is a local measurement and changes across machines.

## Reproduce the ten-seed evaluation

```sh
python -m backend.evaluate --seeds 10 --output artifacts/evaluation.json
python -m backend.benchmark --device CPU --output artifacts/cpu-benchmark.json
```

The evaluation covers five conditions for each of ten seeds. The submitted montage shows the grip-loss recovery condition for all ten seeds. Compare the JSON groups for the recovery-disabled ablation.

## Limits

This submission uses deterministic control in a custom simulation fixture. It does not claim a trained VLA integration, a hardware benchmark, or certified safety. Commercial pricing and customer demand are hypotheses.
