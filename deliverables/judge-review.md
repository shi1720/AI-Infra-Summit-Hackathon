# Independent simulated judge review

**Project:** Granted Robotics, by Shivam Gupta  
**Review date:** September 16, 2026  
**Basis:** The full Intel online challenge brief, current source, committed physics and policy evaluation records, local browser tests, and the production build. This is an internal assessment, not an official judge's score or a promise of eligibility.

## Verdict

Granted has a polished, useful recovery workbench and genuine MuJoCo/OpenVINO evidence. Its strongest contribution is an inspectable recovery experiment with a clear ablation, not a general-purpose table-setting VLA. Against the specific Intel rubric, there are material scope and hardware gaps. Excellent presentation cannot erase those gaps.

**Estimated strict-rubric score: 49/100, with roughly 43 to 60 plausible depending on how much credit judges give a narrow related-policy prototype.** The missing required Intel Core Ultra demonstration could be treated as a compliance issue independent of the numerical score. This review does not assume the project qualifies simply because it uses OpenVINO.

## Criterion scores

| Criterion | Estimate | Evidence and deduction |
| --- | ---: | --- |
| End-to-end task completion and bimanual manipulation | **15/30** | Real dual SO101 kinematics, MuJoCo execution, simultaneous cup/bowl placement, recovery, and verification are implemented. The action space is one fixed two-object placement task. There is no drawer operation, utensil retrieval, hand-off, or pouring. Weld grasps and disabled arm mesh contact checks substantially simplify manipulation. |
| VLA / multimodal reasoning | **8/20** | A real rendered image and instruction can be validated by a constrained multimodal provider. The trained OpenVINO joint-proposal model is genuine. However, the model validates a known scene and fixed plan; it does not infer control poses or dynamically choose an extended action sequence. Motion uses simulator ground truth. The policy learns a local inverse-kinematics mapping and needs mandatory numerical correction. This is not an end-to-end trained VLA. |
| Robustness and generalization | **9/15** | Fifty real runs cover ten matched seeds and five fault/recovery conditions. Position, mass, friction, cylinder dimensions, lighting, and table color vary. Recovery completes 10/10 grip-loss trials versus 0/10 without recovery; obstacles block 10/10. The perturbation ranges are narrow, geometry stays within one family, and the control policy does not depend on visual perception, so lighting/background variation does not establish visual robustness. |
| OpenVINO and Intel Core Ultra optimization | **5/20** | A learned FP32 policy and geometric monitor compile to OpenVINO. There are host-specific latency measurements, numerical equivalence checks, a policy ablation, and CPU/GPU/NPU benchmark tooling. The frozen evidence comes from an Apple arm64 development machine. No final Intel Core Ultra Series 2/3 demonstration, iGPU/NPU result, quantization comparison, or target-device preservation-of-quality result has been verified in this review. |
| Technical quality and reproducibility | **8/10** | Clear source, training artifacts, IR files, model limitations, evaluation scripts, robot asset provenance, API validation, and exported evidence exist. Independent rerun: all 29 backend tests pass; production frontend builds. Browser-only illustration is labeled separately. Dependencies have compatibility ranges and a reference environment freeze rather than a universal installation lock. Run persistence and authorization are demo-grade. |
| Innovation and technical demonstration | **4/5** | The recovery-centered narrative, matched-seed on/off comparison, actual evidence downloads, and clear interface distinguish it from a generic chatbot demo. The underlying control methods are established, and commercial demand has not yet been validated. |
| **Total** | **49/100** | Strict assessment against the published partner rubric, not a generic app-quality score. |

## Verified final evidence

The final source evidence and corresponding `public/evidence/` copies were compared byte-for-byte and matched during this review. The public build was regenerated after the synchronization.

- `evaluation.json`: 50 actual trials, 10 seeds, five conditions.
- Grip-loss recovery: **10/10 completed**, **14.05 mm** mean cup error.
- Grip loss without recovery: **0/10 completed**, **160.96 mm** mean cup error.
- Nominal and object-displacement recovery conditions: **10/10 completed each**.
- Obstacle condition: **10/10 blocked**, which is the expected response rather than a task-completion success.
- `policy-evaluation.json`: mean corrective IK iterations change from **4528.1 to 4288.2**, a **5.3%** reduction in the matched-seed test. Both controller variants complete 10/10 trials.
- Policy training: **480 training demonstrations and 120 held-out examples**; held-out prediction error does not by itself establish task success.
- Final geometry randomization: cylinder radius and height **0.92× to 1.08×** nominal, not alternate shape families.
- Final videos: actual rendered SO101 recovery and ten-seed montage copied to the public evidence directory.
- Backend tests: **29 passed**, with two dependency deprecation warnings, in this independent review.

The Evaluation screen reads measurements from those JSON artifacts. It does not invent benchmark numbers in the component. The live comparison makes two actual API calls with matching seed/fault and different recovery flags. A runtime error is shown as an error; it is not replaced with a successful browser simulation.

## Most valuable remaining fixes

These are ordered by likely judging impact, not implementation convenience.

1. **Resolve the target-hardware evidence gap if an actual appropriate machine is already available.** Run the provided validation script, retain exact device names and errors, and attach the results. An Intel Xeon host or an unavailable NPU is not equivalent to a Core Ultra demonstration. If it cannot be done, state the gap plainly instead of relabeling ARM results.
2. **Use the final synchronized evidence everywhere.** The app, deck, narration, README, and submission must agree on 14.05/160.96 mm and the 5.3% IK-iteration result. A README timing discrepancy was reported to the main agent. Avoid repeating component latency in the pitch unless its exact host and scope are given.
3. **Show one actual image-to-result API run in the final video.** Include the raw observation image, provider/provenance label, actual MuJoCo result, recovery comparison, and then the ten-seed montage. Do not substitute the attractive SVG animation for physics evidence.
4. **Lead with the demonstrated narrow contribution.** Say “an auditable recovery workbench for a fixed bimanual cup-and-bowl task.” Describe drawer, hand-off, pouring, visual pose estimation, and extended VLA capability as future work. Claiming the full dinner-table sequence would lower credibility.
5. **Preserve a failure in the demonstration.** A blocked obstacle or recovery-disabled failed placement is valuable evidence that the interface is reporting outcomes honestly. Show it alongside the successful recovery.
6. **Keep the commercial claim falsifiable.** The next milestone is a paid integrator pilot measuring debugging time or avoided regressions. There is currently no proof of demand, contracted revenue, or validated pricing. The attractive workbench is not yet a production multi-tenant SaaS.

A credible learned hand-off or full camera-driven manipulation pipeline is not a safe last-minute addition. It needs training, validation, and genuine evidence. Under the remaining deadline, coherent evidence and exact claims are more valuable than untested scope expansion.

## App review

The workbench's desktop and 390-pixel mobile layouts were inspected. Mobile document width equaled viewport width, with no horizontal page overflow. Local end-to-end browser tests covered plan generation, fault hold, recovery, completed history, and a live matched-seed backend comparison. The sign-in failure path returns a useful error. Modal Escape handling, keyboard focus containment, accessible input labels, and pending-action states are implemented.

The application offers Firebase Authentication, but run history is browser-local and is not tenant-isolated server storage. The API retains a bounded number of runs in memory. Those facts are disclosed. This review did not independently create a successful new account, certify production security, run the workload on Intel Core Ultra, or verify the final external submission state.

The footer now distinguishes an illustrative preview from actual backend evidence, signed-in identity appears in the workspace selector, and the replay caption correctly calls the grasp a weld abstraction. No critical app bug was found in this review that required changing the underlying execution flow.
