# Granted Robotics demo narration

Synthetic narration in the supplied video. Shivam can also read this script verbatim.

## Scene 1

A robot setting a table looks impressive. But move a cup after the plan starts, and the real test begins. Can it notice the change, stop an unsafe action, and still finish the job? This is Granted Robotics, created by Shivam Gupta.

## Scene 2

For robotics teams, the difficult work often starts after a demonstration fails. What changed? Which action caused the problem? Did the recovery actually complete the task? Granted makes that investigation visible through a familiar two arm table setting scenario.

## Scene 3

The workbench puts the mission, workspace, and execution evidence together. A reviewer can explore the task, inspect a disturbance, and understand the recovery sequence. The goal is to make the important decisions readable, instead of asking a judge to trust a success animation.

## Scene 4

Under the interface, a Python backend uses MuJoCo for articulated arms, tabletop objects, and simulated grasp constraints. An OpenVINO graph evaluates geometric safety signals. The browser is the presentation layer. Simulation evidence is separate from that visual explanation.

## Scene 5

Across ten randomized seeds, grip loss completed ten out of ten times with recovery, and zero out of ten without it. We varied object placement, mass, and friction. These are fifty local simulation runs, with deterministic control. We have not yet demonstrated on Intel Core Ultra hardware.

## Scene 6

The first customer hypothesis is robotics integrators. A paid pilot would import one task and reproduce its recurring failures. We would measure engineering time spent diagnosing regressions. A five hundred dollar monthly workspace is a pricing experiment, not a claim of customer demand or revenue.

## Scene 7

Granted Robotics makes the recovery part of the product. It gives teams a clear place to inspect what failed, how the system responded, and what the evidence supports. Explore the workbench and the open source implementation. Created by Shivam Gupta for the AI Infra Summit Hackathon.
