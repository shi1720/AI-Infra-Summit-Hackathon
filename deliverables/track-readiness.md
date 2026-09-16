# Intel online track readiness

The published track brief asks for dual SO-101 manipulation, camera-based multimodal reasoning, training or fine-tuning, randomized evaluation over 10 seeds, and a final demonstration on Intel Core Ultra Series 2/3. This prototype must not be described as fully meeting that specification.

## Implemented foundation

- A public recovery workbench and reproducible Python simulation source.
- MuJoCo object manipulation, fault injection, recovery, and JSON evidence.
- An OpenVINO geometric safety graph, with local timing evidence.
- A constrained camera and language validator, a learned state-based joint-target proposal model, and mandatory numerical correction.

## Material gaps

- No final demonstration on Intel Core Ultra Series 2/3 has been performed. Development-machine timings are not Intel Core Ultra benchmark results.
- The geometric OpenVINO graph is not a trained VLA policy and does not establish model optimization quality for a VLA.
- The project trains a small joint-target imitation model and exports it to OpenVINO. It does not claim end-to-end VLA training or fine-tuning.
- The current table-setting fixture is narrower than the full drawer, utensils, hand-off, and pouring sequence in the brief.
- A 50-run evaluation across 10 seeds now exists using MuJoCo Menagerie SO101 arms. Randomization covers small position perturbations, mass, friction, cylinder radius and height, lighting, and table color. Generalization to novel objects or tasks is not demonstrated.

The submission should present its actual contribution and these gaps honestly. No eligibility or track-compliance guarantee is made.
