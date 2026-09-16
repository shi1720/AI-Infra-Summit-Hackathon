import { useEffect, useState } from "react";
import {
  ArrowDownToLine,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  FlaskConical,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
type EvalRun = {
  seed: number;
  fault: string;
  recovery_enabled: boolean;
  status: string;
  metrics: {
    placement_error_mm: Record<string, number>;
    compute_ms: number;
    physics_steps: number;
    recoveries: number;
  };
  perturbations: Record<string, unknown>;
};
type EvaluationData = {
  robot: string;
  host: { platform: string; processor: string; intel_hardware: boolean };
  seed_count: number;
  total_runs: number;
  randomization: string;
  groups: Record<
    string,
    {
      runs: number;
      completed: number;
      blocked: number;
      mean_cup_error_mm: number;
      mean_compute_ms: number;
    }
  >;
  monitor_benchmark: {
    engine: string;
    precision: string;
    warmup: number;
    samples: number;
    p50_ms: number;
    p95_ms: number;
    serial_inferences_per_second: number;
    max_abs_distance_error_m: number;
    scope: string;
  };
  runs: EvalRun[];
};
type PolicyData = {
  training: {
    model: string;
    training_samples: number;
    heldout_samples: number;
    heldout_joint_rmse_rad: number;
    heldout_joint_mae_rad: number;
    deployment: string;
    limitations: string;
  };
  groups: Record<
    string,
    {
      successes: number;
      trials: number;
      mean_ik_iterations: number;
      mean_compute_ms: number;
      mean_cup_error_mm: number;
    }
  >;
  policy_benchmark: { engine: string; p50_ms: number; p95_ms: number };
  limitations: string;
};
const labels: Record<string, string> = {
  none: "Nominal placement",
  object_displaced: "Object displaced",
  grip_loss: "Grip lost",
  obstacle: "Workspace obstacle",
};
export default function Evaluation({ onStart }: { onStart: () => void }) {
  const [policy, setPolicy] = useState<PolicyData | null>(null);
  useEffect(() => {
    fetch("/evidence/policy-evaluation.json?v=37d69daabfec", {
      cache: "no-store",
    })
      .then((r) => (r.ok ? r.json() : null))
      .then(setPolicy)
      .catch(() => setPolicy(null));
  }, []);
  const [data, setData] = useState<EvaluationData | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<EvalRun | null>(null);
  useEffect(() => {
    fetch("/evidence/evaluation.json?v=ba8460bf7fba", { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error("Evidence could not load");
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);
  return (
    <div className="content evaluation">
      <div className="page-heading">
        <div>
          <div className="eyebrow">MEASURED. REPRODUCIBLE. BOUNDED.</div>
          <h1>
            Trust has a paper trail<span>.</span>
          </h1>
          <p>A matched-seed evaluation of failure detection and recovery.</p>
        </div>
        <a
          className="button secondary"
          href="/evidence/evaluation.json"
          download
        >
          <ArrowDownToLine size={15} />
          Download raw results
        </a>
      </div>
      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}
      {!data && !error && (
        <div className="empty-plan">Loading recorded evaluation evidence…</div>
      )}
      {data && (
        <>
          <div className="evaluation-callout">
            <FlaskConical size={22} />
            <div>
              <strong>
                {data.total_runs} actual physics runs. {data.seed_count} matched
                seeds. Five conditions.
              </strong>
              <p>
                Recorded MuJoCo evaluation on {data.host.processor}. Results
                below are read from the committed evidence file, not generated
                from the illustration.
              </p>
            </div>
            <span className="badge">RECORDED EVIDENCE</span>
          </div>
          <div className="evaluation-hero">
            <div>
              <div className="eyebrow">THE RECOVERY ABLATION</div>
              <h2>
                Same fault. Same seeds.
                <br />A different outcome.
              </h2>
              <p>
                Grip loss is injected during transport. With recovery, the robot
                re-localizes and re-grasps. Without it, placement fails
                verification.
              </p>
              <button className="button primary" onClick={onStart}>
                Reproduce a live comparison <ArrowRight size={15} />
              </button>
            </div>
            <div className="ablation-chart">
              {[
                ["grip_loss:recovery=True", "Recovery enabled"],
                ["grip_loss:recovery=False", "Recovery disabled"],
              ].map(([key, label]) => {
                const d = data.groups[key];
                return (
                  <div key={key}>
                    <div className="bar-label">
                      <span>{label}</span>
                      <strong>
                        {d.completed}/{d.runs}
                      </strong>
                    </div>
                    <div className="ablation-track">
                      <div
                        style={{ width: `${(d.completed / d.runs) * 100}%` }}
                      />
                    </div>
                    <small>
                      {d.mean_cup_error_mm.toFixed(2)} mm mean cup placement
                      error
                    </small>
                  </div>
                );
              })}
              <p>
                Completion means both objects meet the simulator's placement
                tolerance. This small controlled evaluation does not establish
                real-world reliability.
              </p>
            </div>
          </div>
          <section className="eval-section">
            <div className="eval-section-heading">
              <div>
                <span className="eyebrow">01 / CONDITION MATRIX</span>
                <h2>Every failure mode has an expected response.</h2>
              </div>
              <span className="badge">10 SEEDS PER CONDITION</span>
            </div>
            <div className="table-scroll">
              <table className="eval-table">
                <thead>
                  <tr>
                    <th>Condition</th>
                    <th>Recovery</th>
                    <th>Completed</th>
                    <th>Blocked</th>
                    <th>Mean cup error</th>
                    <th>Mean compute</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.groups).map(([key, g]) => (
                    <tr key={key}>
                      <td>{labels[key.split(":")[0]]}</td>
                      <td>
                        <span className="badge">
                          {key.endsWith("True") ? "Enabled" : "Disabled"}
                        </span>
                      </td>
                      <td>
                        <span
                          className={
                            g.completed === g.runs ? "value-green" : ""
                          }
                        >
                          {g.completed} / {g.runs}
                        </span>
                      </td>
                      <td>
                        {g.blocked} / {g.runs}
                      </td>
                      <td>{g.mean_cup_error_mm.toFixed(2)} mm</td>
                      <td>{g.mean_compute_ms.toFixed(2)} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="eval-note">
              <ShieldCheck size={16} />
              <span>
                An obstacle should prevent completion. All{" "}
                {data.groups["obstacle:recovery=True"].blocked} obstacle trials
                were blocked by the safety gate.
              </span>
            </div>
          </section>
          <div className="eval-detail-grid">
            <section className="eval-section">
              <span className="eyebrow">02 / EXPERIMENT DESIGN</span>
              <h2>Small perturbations. Controlled comparisons.</h2>
              <dl className="provenance">
                <dt>Robot</dt>
                <dd>{data.robot}</dd>
                <dt>Seeds</dt>
                <dd>
                  0 through {data.seed_count - 1}, identical across conditions
                </dd>
                <dt>Object XY position</dt>
                <dd>±8 mm per axis, per object</dd>
                <dt>Object mass</dt>
                <dd>0.8× to 1.2× nominal mass</dd>
                <dt>Sliding friction</dt>
                <dd>0.8× to 1.2× nominal friction</dd>
                <dt>Object geometry</dt>
                <dd>
                  Cylinder radius and height 0.92× to 1.08× nominal. No
                  alternate shape families.
                </dd>
                <dt>Scene appearance</dt>
                <dd>
                  Light diffuse/ambient and table background RGB vary by seed.
                  The controller still uses ground-truth poses.
                </dd>
                <dt>Full configuration</dt>
                <dd>{data.randomization}</dd>
                <dt>Grasp mechanism</dt>
                <dd>
                  Simulated weld attachment, not finger-contact validation
                </dd>
                <dt>Reproduce</dt>
                <dd>
                  <code>python -m backend.evaluate --seeds 10</code>
                </dd>
              </dl>
            </section>
            <section className="eval-section">
              <span className="eyebrow">03 / OPENVINO MONITOR</span>
              <h2>
                Measure the component.
                <br />
                Name the limits.
              </h2>
              <div className="monitor-numbers">
                <div>
                  <strong>
                    {data.monitor_benchmark.p50_ms.toFixed(5)}
                    <small> ms</small>
                  </strong>
                  <span>p50 geometric inference</span>
                </div>
                <div>
                  <strong>
                    {data.monitor_benchmark.p95_ms.toFixed(5)}
                    <small> ms</small>
                  </strong>
                  <span>p95 geometric inference</span>
                </div>
              </div>
              <dl className="provenance">
                <dt>Engine</dt>
                <dd>{data.monitor_benchmark.engine}</dd>
                <dt>Precision</dt>
                <dd>{data.monitor_benchmark.precision}</dd>
                <dt>Samples</dt>
                <dd>
                  {data.monitor_benchmark.warmup} warmups +{" "}
                  {data.monitor_benchmark.samples.toLocaleString()} measured
                  inferences
                </dd>
                <dt>Device</dt>
                <dd>
                  {data.host.processor} CPU. Intel hardware:{" "}
                  {data.host.intel_hardware ? "yes" : "no"}.
                </dd>
                <dt>Max absolute error</dt>
                <dd>
                  {data.monitor_benchmark.max_abs_distance_error_m.toExponential(
                    3,
                  )}{" "}
                  m against reference distance
                </dd>
              </dl>
              <p className="scope-warning">
                <TriangleAlert size={15} />
                {data.monitor_benchmark.scope}.
              </p>
            </section>
          </div>
          <section className="eval-section">
            <div className="eval-section-heading">
              <div>
                <span className="eyebrow">04 / THE RAW RUNS</span>
                <h2>No averages without the underlying evidence.</h2>
              </div>
              <select
                aria-label="Filter evaluation runs"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All 50 runs</option>
                <option value="none">Nominal</option>
                <option value="object_displaced">Object displaced</option>
                <option value="grip_loss">Grip loss</option>
                <option value="obstacle">Obstacle</option>
              </select>
            </div>
            <div className="table-scroll run-table">
              <table className="eval-table">
                <thead>
                  <tr>
                    <th>Seed</th>
                    <th>Condition</th>
                    <th>Recovery</th>
                    <th>Outcome</th>
                    <th>Cup / bowl error</th>
                    <th>Inspect</th>
                  </tr>
                </thead>
                <tbody>
                  {data.runs
                    .filter((r) => filter === "all" || r.fault === filter)
                    .map((r, i) => (
                      <tr key={i}>
                        <td>{r.seed.toString().padStart(2, "0")}</td>
                        <td>{labels[r.fault]}</td>
                        <td>{r.recovery_enabled ? "On" : "Off"}</td>
                        <td>
                          <span className={"outcome " + r.status}>
                            {r.status}
                          </span>
                        </td>
                        <td>
                          {r.metrics.placement_error_mm.cup.toFixed(2)} /{" "}
                          {r.metrics.placement_error_mm.bowl.toFixed(2)} mm
                        </td>
                        <td>
                          <button
                            className="text-button"
                            onClick={() =>
                              setSelected(selected === r ? null : r)
                            }
                            aria-label={`Inspect seed ${r.seed} ${r.fault} recovery ${r.recovery_enabled}`}
                          >
                            <ChevronDown size={15} />
                          </button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            {selected && (
              <pre className="run-json">
                {JSON.stringify(selected, null, 2)}
              </pre>
            )}
          </section>
          <section className="eval-section">
            <span className="eyebrow">05 / LEARNED POLICY ABLATION</span>
            <h2>A learned proposal, followed by mandatory correction.</h2>
            {policy ? (
              <>
                <p className="policy-description">
                  {policy.training.model}. Trained on{" "}
                  {policy.training.training_samples} inverse-kinematics
                  demonstrations, with {policy.training.heldout_samples} held
                  out. The policy predicts a joint target that initializes a
                  numerical pose correction. It does not learn vision or
                  language.
                </p>
                <div className="table-scroll">
                  <table className="eval-table">
                    <thead>
                      <tr>
                        <th>Controller</th>
                        <th>Completed</th>
                        <th>Mean IK iterations</th>
                        <th>Mean cup error</th>
                        <th>Mean compute</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(policy.groups).map(([name, g]) => (
                        <tr key={name}>
                          <td>
                            {name === "ik_only"
                              ? "Numerical IK only"
                              : "Learned proposal + correction"}
                          </td>
                          <td>
                            {g.successes}/{g.trials}
                          </td>
                          <td>{g.mean_ik_iterations.toFixed(1)}</td>
                          <td>{g.mean_cup_error_mm.toFixed(2)} mm</td>
                          <td>{g.mean_compute_ms.toFixed(2)} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="policy-facts">
                  <div>
                    <strong>
                      {(
                        (1 -
                          policy.groups.learned_plus_correction
                            .mean_ik_iterations /
                            policy.groups.ik_only.mean_ik_iterations) *
                        100
                      ).toFixed(1)}
                      %
                    </strong>
                    <span>
                      fewer mean IK iterations in this matched-seed test
                    </span>
                  </div>
                  <div>
                    <strong>
                      {policy.training.heldout_joint_mae_rad.toFixed(4)} rad
                    </strong>
                    <span>held-out mean absolute joint prediction error</span>
                  </div>
                  <div>
                    <strong>
                      {policy.policy_benchmark.p50_ms.toFixed(5)} ms
                    </strong>
                    <span>p50 learned-policy OpenVINO inference</span>
                  </div>
                </div>
                <p className="policy-description">{policy.limitations}</p>
                <p className="policy-description">
                  Deployment: {policy.training.deployment}. Joint prediction
                  error alone is not a task-success metric.
                </p>
              </>
            ) : (
              <p className="policy-description">
                Policy evidence can be downloaded below.
              </p>
            )}
            <a
              className="text-link"
              href="/evidence/policy-evaluation.json"
              download
            >
              <ArrowDownToLine size={14} />
              Download policy training and evaluation evidence
            </a>
          </section>
          <section className="limits-box">
            <TriangleAlert size={20} />
            <div>
              <h3>What these results do not prove</h3>
              <p>
                Ten seeds are insufficient to estimate production reliability.
                Object poses are simulator ground truth. Grasping uses weld
                constraints, robot mesh collision contacts are disabled, and
                safety checks monitor gripper separation rather than full-body
                collisions. OpenVINO runs a geometric monitor and a small
                state-based joint proposal model with corrective IK, not an
                end-to-end learned VLA policy. Results were measured on an ARM
                Mac, not an Intel device. Hardware safety and generalization to
                unseen tasks remain unvalidated.
              </p>
            </div>
          </section>
          <div className="eval-downloads">
            <a href="/evidence/evaluation.json" download>
              <ArrowDownToLine size={16} />
              50-run evidence
            </a>
            <a href="/evidence/so101-recovery.json" download>
              <ArrowDownToLine size={16} />
              Full recovery trajectory
            </a>
            <a
              href="/evidence/ten-seed-montage.mp4"
              target="_blank"
              rel="noreferrer"
            >
              <FlaskConical size={16} />
              Ten-seed video
            </a>
          </div>
          <p className="platform-note">Recorded host: {data.host.platform}</p>
        </>
      )}
    </div>
  );
}
