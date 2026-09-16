# Commercial hypothesis

Granted Robotics would sell reproducible recovery testing to robotics integrators. The initial buyer is a small engineering team deploying manipulation systems at customer sites. The initial problem is the time spent reproducing intermittent failures and explaining whether a change improved reliability.

## Proposed pilot

Import one tabletop task, define a fixed set of disturbances, and compare two policy versions. Measure engineer time per diagnosed regression, task completion, intervention count, and unsafe proposals blocked. A pilot succeeds only if the team can reproduce failures faster and understand the result without extra manual analysis.

## Pricing experiment

Test a $500 per month team workspace with local execution and shared reports. This is a proposed price, not validated willingness to pay. At an assumed fully loaded engineering cost of $75 per hour, saving seven hours a month would cover that fee. Both inputs require customer validation.

## Costs

The current web demonstration can run on static hosting. Local simulation uses the participant's CPU and does not require paid language-model calls. Optional cloud inference or hosted simulation introduces usage costs and would need quotas, billing, and workload isolation before a commercial release. Free hosting allowances are provider-dependent and may change.

## Competitive position

Simulation platforms and robotics evaluation tools already exist. Our proposed differentiation is a small, readable workflow for recovery regression: define the disturbance, observe the intervention, and export the evidence. We have not established a defensible moat. A future advantage could come from task-specific failure libraries and customer integrations, with appropriate rights to use that data.

## Boundaries

No customers, revenue, real-world safety certification, or measured customer savings are claimed. Hardware validation, authenticated shared workspaces, and a trained VLA integration are future work unless explicitly shown in the final repository.
