# Granted Robotics full demonstration

Verbatim narration. The supplied video uses a synthetic voice.

## Scene 1

A robot setting a table looks impressive. But a moved cup or a failed grasp can break that plan. Granted Robotics makes the recovery inspectable. Created by Shivam Gupta, it combines a clear operator workbench with reproducible simulation evidence.

## Scene 2

Here is the hosted workbench. Choose the physics backed cup and bowl task, then select grip loss. Validate the task in MuJoCo. The result shows measured placement errors and backend events. The illustration is clearly separate from that evidence. Replay the workflow, inspect the recovery, and export the JSON record. A guest can test the core flow, and Firebase sign in is available.

## Scene 3

The React workbench accepts a task and shows the evidence. A FastAPI service validates requests, then runs the MuJoCo fixture. Optional camera and language validation can approve only the supported contract. The controller and geometric monitor execute the task. Results include events and measured errors.

## Scene 4

A real camera image and instruction go to the constrained language validator. Separately, we trained a small joint target imitation policy on four hundred eighty inverse kinematics examples, with one hundred twenty held out. OpenVINO runs its proposals. Mandatory numerical correction remains part of control. This is not an end to end VLA.

## Scene 5

This is actual MuJoCo rendering, separate from the browser illustration. Both SO101 arms move objects to predefined targets. An injected grip loss breaks the initial attempt. The controller detects the displaced object and follows a recovery path. Simplified grasp attachment and simulator state remain important limitations.

## Scene 6

We evaluated ten seeds in five conditions, for fifty runs. We varied object position, mass, friction, cylinder size, lighting, and table color. Grip loss completed ten out of ten with recovery, and zero without it. All ten obstacle cases blocked execution. A safe stop is reported separately from task completion.

## Scene 7

The per seed records make the result inspectable. Every grip loss recovery trial completed, but errors still vary by initial condition. The comparison shows mean cup error falling from about one hundred sixty millimeters to about fifteen. This is a small controlled benchmark, not generalization to new tasks.

## Scene 8

OpenVINO runs both the geometric graph and the learned joint target policy. In ten recovery trials, learned proposals plus correction reduced average numerical iterations by five point three percent. Both approaches completed every trial. The learned policy median inference was thirty seven microseconds on Apple hardware. Intel validation remains open.

## Scene 9

Twenty nine backend tests pass, covering task rejection, provider failures, safety checks, and learned policy reference accuracy. The repository includes reproducible training, evaluation, and device benchmark commands. The biggest remaining gaps against the brief are an end to end VLA, richer complementary manipulation, and a final Intel Core Ultra demonstration.

## Scene 10

The business starts with a small paid pilot, not a market size claim. We would import one integrator task and its recurring failure cases. We would measure diagnosis time before and after. A five hundred dollar monthly workspace is a pricing test. At an assumed seventy five dollars an engineer hour, seven saved hours covers that fee.

## Scene 11

The next milestone is a policy that reasons directly over vision and language. We also need a richer dual arm task, broader randomization, and an Intel Core Ultra run. Before commercial use, the product needs durable tenant storage, workload controls, and operational monitoring. Hardware safety validation is a separate effort.

## Scene 12

Granted Robotics makes the recovery part of the product. Review the workbench, replay the actual physics, and inspect the per seed records. The repository and demo are public. Created by Shivam Gupta for the AI Infra Summit Hackathon.