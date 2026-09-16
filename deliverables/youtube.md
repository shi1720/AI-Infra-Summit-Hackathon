# YouTube title
Granted Robotics: Robot Recovery, Learned Control and 10-Seed Evidence

# Description
A cup moves. A grasp slips. The plan needs to change.

Granted Robotics is a robotics safety and recovery workbench created by Shivam Gupta for the AI Infra Summit Hackathon. It uses a familiar two-arm table-setting task to make failure detection, action checks, and recovery understandable.

This video shows the product workflow, actual MuJoCo SO101 execution, and a ten-seed recovery montage. Our controlled evaluation includes fifty simulation runs across five conditions. Grip loss completed 10/10 trials with recovery and 0/10 without it. These results come from an Apple development machine. We have not demonstrated on Intel Core Ultra hardware. The project uses a React and TypeScript interface, a Python MuJoCo simulation, a camera-aware constrained language validator, and OpenVINO for geometric checks and learned joint-target proposals. A small imitation model trains on 480 examples, with 120 held out, and runs through OpenVINO with mandatory numerical correction. It is a simulation MVP, not a certified hardware safety system or an end-to-end VLA policy.

Try the workbench: https://granted-robotics.web.app

Source code: https://github.com/shi1720/AI-Infra-Summit-Hackathon

Created by Shivam Gupta with AI-assisted development. Synthetic narration is used in this video.

Chapters
0:00 The problem
0:15 Hosted product walkthrough
0:38 Architecture
0:58 Camera input and learned control
1:19 Actual MuJoCo recovery
1:39 50-run evaluation
2:01 Ten-seed motion montage
2:19 OpenVINO and paired results
2:41 Tests and rubric gaps
3:04 Commercial pilot hypothesis
3:25 Limitations and roadmap
3:45 Try Granted Robotics

#AIInfraSummit #Robotics #MuJoCo #OpenVINO #Hackathon
