# Testing Granted Robotics

Application: https://granted-robotics.web.app
Repository: https://github.com/shi1720/AI-Infra-Summit-Hackathon

## Browser walkthrough

1. Open the app in a recent desktop or mobile browser. Guest access works without an account. Firebase email sign-in is optional.
2. Choose **Serve with confidence**. Use the exact task: **Set the table with a cup and bowl**.
3. Select **Grip lost during placement**, leave recovery enabled, and click **Validate in MuJoCo**.
4. Inspect **Physics evidence**. It reports actual backend completion, placement errors, physics steps, recovery events, camera validation, and the joint proposal policy.
5. Click **Approve playback** to see the separate explanatory animation. Inspect its hold and approve recovery.
6. Export the JSON evidence or open the completed record in **Run history**. History is local to this browser.
7. Open **Evaluation** for the 50-run condition matrix and per-seed records. Try **Compare recovery on / off** to execute a live paired experiment.
8. Expand **See the real physics** to watch an actual MuJoCo recording. It is separate from the browser illustration.

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

This submission uses learned state-based proposals and mandatory numerical correction in a MuJoCo SO101 fixture. It does not claim a trained VLA integration, a hardware benchmark, or certified safety. Commercial pricing and customer demand are hypotheses.
