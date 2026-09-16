# Granted Robotics

**Permission to act. Evidence to trust.**

Created by Shivam Gupta for the AI Infra Summit Hackathon.

## Inspiration

A robot setting a table looks impressive until a cup moves after the plan starts. The real product question begins there: can it notice the change, stop an unsafe action, and finish the job with evidence of what happened?

Granted Robotics explores that overlooked layer of physical AI. We chose a familiar bimanual table-setting task so anyone can understand the failure, then built a workbench around the recovery. Our starting customer hypothesis is robotics integrators who need repeatable tests before they put a policy near expensive hardware.

## What it does

Granted Robotics lets a reviewer configure a table-setting mission, inspect a simulated two-arm workspace, and investigate how disturbances affect execution. The workbench makes action checks and recovery decisions visible rather than hiding them behind a success animation.

The local backend uses MuJoCo for physics. An OpenVINO graph evaluates geometric safety signals. The system keeps the simulation and the user interface separate so recorded evidence can remain available even when a compute service is offline.

The project is a simulation MVP. Its learned joint-target proposals still require numerical correction and do not form an end-to-end vision-language-action model, and its checks are not a certification that a physical robot is safe. The repository explains these boundaries explicitly.

## How we built it

The interface uses React and TypeScript. The Python backend models two SO101 articulated arms from MuJoCo Menagerie, tabletop objects, inverse-kinematics targets, and simulated grasp constraints in MuJoCo. Disturbance scenarios exercise failure detection and recovery behavior. OpenVINO runs both the geometric safety graph and a small learned joint-target model. We trained that model on 480 inverse-kinematics demonstrations and held out 120. Its proposals initialize mandatory numerical correction. In a paired ten-seed comparison, the learned initialization reduced numerical iterations by about 5.3%, with both controllers completing every trial.

We designed the product around evidence: a reviewer should understand the requested task, the disturbance, the intervention, and the resulting outcome. The first deployment keeps infrastructure small and provides a public web interface without requiring a paid model API to inspect the core demonstration.

Shivam Gupta created this project with AI-assisted development. Our priority was an inspectable implementation, clear product boundaries, and a demo that a judge can reproduce.

## Challenges we ran into

The hardest challenge was separating a compelling visual explanation from actual robotics evidence. A browser animation can show an intended motion, but only execution data can establish what the physics engine did. We therefore distinguish the presentation layer from backend simulation and avoid treating a replay as a live robot run.

The final implementation uses SO101 assets and includes an optional camera-aware language planner. We did not train a VLA policy, and we did not have an Intel Core Ultra system for the final demonstration. Those remain material gaps against the full track specification.

Another challenge was defining useful safety checks without overstating them. Geometric clearance is one signal. Real deployments also need force limits, perception uncertainty, hardware interlocks, and validation for the specific robot and environment.

## Accomplishments that we're proud of

Our final local evaluation ran ten seeds across five conditions, for fifty simulations. Grip-loss recovery completed ten out of ten trials, while the same fault without recovery completed zero. Nominal and displaced-object runs also completed ten out of ten. The obstacle cases stopped safely in all ten trials. We randomized placement by +/-8 mm and mass and sliding friction by 0.8x to 1.2x, plus cylinder radius and height by +/-8%, lighting, and table color. These are bounded fixture results on an Apple development machine, not Intel Core Ultra validation or real-world reliability claims.

We made a technical infrastructure problem understandable through an everyday task. A displaced object and a failed grasp show why recovery belongs in the product, not just in an error log.

We also made the intended commercial path concrete: help an integrator turn a customer's recurring failure cases into reproducible regression tests before another deployment. The business hypothesis is measurable through engineering time saved and repeat failures avoided.

## What we learned

A robot's success rate is only part of the story. Operators also need to know whether the system recognized a failure, why it chose a recovery, and whether that recovery actually satisfied the original task.

Infrastructure earns trust when it exposes its limits. A small reproducible experiment is more useful than a large unsupported claim.

## What's next for Granted Robotics

The next technical milestone is connecting an end-to-end VLA policy to the same evaluation interface, then comparing its behavior with and without action checks across a fixed disturbance suite. We also plan richer perception inputs and hardware-specific safety constraints.

The first commercial experiment would be a paid pilot with a robotics integrator: import one existing task, reproduce their most frequent failure cases, and measure the time needed to diagnose a regression. Pricing and customer demand remain hypotheses until those pilots provide evidence.
