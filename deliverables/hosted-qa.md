# Final hosted application QA

URL: https://granted-robotics.web.app  
Date: September 16, 2026  
Method: a separate Chrome tab controlled through the browser UI, with responsive viewport inspection. This report records observed outcomes and does not certify production readiness.

## Checks

| Check | Observed result |
| --- | --- |
| Desktop initial load | Passed. Current UI, exact supported default instruction, seed and recovery controls rendered. |
| Live request | Passed. Submitted `Set the table with a cup and bowl`, seed 42, grip-loss fault, recovery enabled through the hosted UI. |
| Physics outcome | 2/2 objects verified, 13.97 / 13.24 mm cup/bowl error, 8,441 physics steps, one recovery. |
| Multimodal provenance | UI reports `OpenAI constrained language planner` and `rendered MuJoCo RGB validated by language model`. |
| Learned runtime provenance | UI reports `OpenVINO CPU learned polynomial imitation policy (FP32)` and mandatory numerical pose correction. |
| Actual camera observation | Expanded the observation disclosure. The actual PNG loaded with natural dimensions 640 × 480 and a data-URI source. Its rendered SO101 scene was visually inspected. |
| Frozen evaluation | Hosted Evaluation displays 14.05 mm with recovery, 160.96 mm without recovery, and 5.3% fewer corrective IK iterations. The stale 13.81 value is absent. |
| Desktop presentation | Workcell evidence and Evaluation layout inspected. No visible blocking layout issue. |
| Mobile Evaluation | Inspected at 390 × 844. Document width and body width both equal 390 pixels, with no horizontal page overflow. |
| Mobile navigation | Menu opens; choosing Workcell closes the drawer. Workcell document width remains 390 pixels. |
| Browser errors | The final hosted QA tab's captured error-level browser log is empty. |
| Test cleanup | Temporary viewport override reset to the normal desktop size. |

No app changes were made during this final hosted check. One non-blocking accessibility improvement remains: the mobile menu icon button should have an explicit accessible name. The menu works visually and through pointer interaction.

## Scope limits

This compact check did not repeat a successful new-account signup, perform a security penetration test, validate physical hardware, or verify an Intel Core Ultra deployment. It also does not establish that the hackathon or video submission has completed. The app distinguishes its illustrated playback from the backend evidence; the camera image and measurements above came from the actual hosted request.
