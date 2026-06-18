# Rough Paper Drafts — Prime Candidates

> Status: rough drafts for advisor/collaborator review. Gap statements reflect
> all-timespan literature verification from deep-research run (2026-06-17).
> DOIs are cited where verified; mark [VERIFY] before submission.

---

## DRAFT 1 (Rank #1) — A01+A04 Combined
### P-V Hysteresis as a Fatigue Leading Indicator and Its Degradation of Pressure-Only Proprioception in Shared-Manifold Soft Grippers

**Target venue:** Soft Robotics (Mary Ann Liebert) | IEEE RA-L  
**Estimated length:** 8 pages + supplementary  
**Hardware cost:** ~$320

---

**Abstract (draft)**

Soft pneumatic grippers present two concurrent monitoring challenges: detecting actuator fatigue before rupture and reconstructing gripper pose from existing pressure signals without additional sensors. Prior work addresses each in isolation. We show that a shared pneumatic manifold—the most practical topology for multi-finger grippers—creates a third, previously uncharacterized challenge: inter-chamber pressure cross-talk couples both problems. We fabricate a three-chamber silicone gripper on a shared manifold and make two contributions. First, we demonstrate that pressure-volume (P-V) hysteresis loop shape is a reliable leading indicator of silicone actuator fatigue, with measurable loop-shape change detectable [X] cycles before mechanical rupture (mean ± std, N=10). Second, we show that shared-manifold cross-talk degrades pressure-only pose reconstruction accuracy from [A]% to [B]%, and that a cross-talk correction model recovers accuracy to within [C]% of the isolated-chamber baseline. We further characterize how fatigue-induced P-V drift and proprioceptive-accuracy degradation are coupled: as an actuator ages, the P-V signature shift that signals fatigue also shifts the cross-talk correction model, causing both to fail simultaneously. Joint monitoring from the same pressure stream is therefore necessary and sufficient for health-aware soft gripper autonomy.

---

**1. Introduction**

Soft pneumatic actuators are increasingly deployed in grippers, medical devices, and wearable systems due to their compliance and safety. Two monitoring problems arise in practice. The first is health monitoring: silicone actuators fail by cyclic fatigue, but current practice detects failure only after rupture. The second is proprioception: knowing the gripper's pose without expensive external sensors is essential for closed-loop control. Recent work showed that control-loop pressure readings can reconstruct pose in isolated single-chamber or independently-driven multi-chamber designs [Wang et al., Soft Robotics 2023, DOI 10.1089/soro.2021.0056; Wang et al., Adv. Intell. Syst. 2025, arXiv:2411.07309]. However, these designs assume each chamber's pressure is independently controllable. In practice, multi-finger grippers share a pneumatic manifold to reduce valve count and system complexity.

We identify a gap: no prior work characterizes how shared-manifold inter-chamber coupling (cross-talk) affects pressure-only proprioception, and no prior work uses the in-loop P-V hysteresis signature as a fatigue leading indicator. We further observe that these two problems are not independent in a shared-manifold system: fatigue changes the P-V signature, which changes the apparent cross-talk pattern, which corrupts the proprioceptive model.

This paper makes three contributions:
1. A cyclic P-V signature dataset for Dragon Skin silicone actuators showing statistically measurable loop-shape change [X] cycles before rupture (N=10 actuators, [N_cycles] total cycles).
2. A cross-talk characterization and correction method for three-chamber shared-manifold grippers, recovering pose reconstruction accuracy from [B]% to [C]% (baseline: [A]%).
3. A joint health-and-pose monitoring framework demonstrating that the two failure modes are coupled and must be tracked from the same pressure stream.

**2. Background and Related Work**

*2.1 Soft Actuator Fatigue*
Roels et al. (Adv. Intell. Syst. 2026, DOI 10.1002/aisy.202500699) established a standardized framework for elastomer characterization but explicitly excluded fatigue. Torzini et al. (2024, DOI 10.1007/s00170-024-14216-0) and Libby et al. (2022, arXiv:2212.03420) report only cycles-to-failure counts or FEM-predicted deviation—neither uses in-loop P-V shape as a health indicator. The closest work in non-soft systems uses acoustic emission for hydraulic actuator health [CITE], but pressure-signal-only health monitoring for silicone pneumatic actuators has not been demonstrated.

*2.2 Pressure-Only Proprioception*
Wang et al. (Soft Robotics 2023) used unified soft-body encoding with an RNN to reconstruct pose from internal pressure on a single-chamber finger. Wang et al. (Adv. Intell. Syst. 2025) demonstrated physical reservoir computing on a fabric arm using only internal pressures. Both designs use isolated chambers. The shared-manifold cross-talk condition—where opening valve i changes pressure in chamber j—has not been studied.

**3. Hardware Design**

*3.1 Gripper Fabrication*
Three-chamber Dragon Skin 20A silicone gripper cast in a [dimensions] mold. Chambers share a single manifold with a solenoid valve per chamber. One Honeywell HSC pressure sensor per chamber (±0.5% FS accuracy).

*3.2 Cycling Jig*
A pneumatic pressure jig cycles each actuator between 0 and [P_max] kPa at [freq] Hz. A solenoid-actuated valve controls inflation/deflation. P-V loops are recorded at 100 Hz.

*3.3 Motion Capture Ground Truth*
A 6-marker Vicon (or OptiTrack) setup records gripper pose at 120 Hz, synchronized with pressure data via hardware trigger.

**4. P-V Fatigue Signature Study**

*4.1 Protocol*
N=10 actuators cycled to failure. P-V loops sampled at [interval]-cycle marks. Rupture defined as >20% pressure drop within one cycle.

*4.2 Signature Features*
Loop area (hysteresis energy), peak pressure, pressure at 80% volume, loop asymmetry ratio, and loop-shape principal component 1 extracted per cycle block.

*4.3 Logistic Degradation Model*
[Model description — fit logistic curve to each feature vs. normalized cycle count, extract lead-time metric: how many cycles before rupture does each feature diverge from healthy baseline by >2σ?]

*4.4 Results (placeholder)*
Table: Feature | Lead-time (cycles) | AUC | p-value
P-V area | TBD | TBD | TBD
Peak pressure | TBD | TBD | TBD
PC1 score | TBD | TBD | TBD

**5. Cross-Talk Characterization and Correction**

*5.1 Cross-Talk Measurement*
With chambers 2 and 3 sealed and valve 1 actuated, measure pressure changes in chambers 2 and 3 vs. chamber 1 command pressure across [N] conditions.

*5.2 Correction Model*
ARX model or ridge regression on [NxM] input vector (all chamber pressures + derivatives) predicting per-chamber true commanded pressure. Compare uncorrected, ARX-corrected, and echo-state network (ESN) outputs.

*5.3 Proprioception Results (placeholder)*
Table: Model | RMSE (mm) | R² | Inference time (ms)
Uncorrected | TBD | TBD | TBD
ARX-corrected | TBD | TBD | TBD
ESN | TBD | TBD | TBD

**6. Coupled Failure Analysis**

Show that at [X]% of actuator life, fatigue-induced P-V drift shifts the cross-talk correction model coefficients by [Y]%, degrading proprioceptive RMSE from [C]% to [D]%. Joint recalibration triggered by the P-V health monitor recovers proprioceptive accuracy.

**7. Discussion**

Limitations: N=10 actuators, single material (Dragon Skin 20A), one gripper geometry. Future work: multi-material comparison (addresses A05), more chamber counts, fatigue-aware adaptive control (addresses N04 idea).

**8. Conclusion**

We demonstrated that P-V hysteresis loop shape predicts silicone actuator fatigue [X] cycles before rupture, and that shared-manifold cross-talk degrades pressure-only proprioception in a characterizable and correctable way. The two phenomena are coupled: joint monitoring from the same pressure stream is both necessary and sufficient for health-aware soft gripper control.

---

## DRAFT 2 (Rank #2) — G02
### Cross-Pattern and Cross-Material Fatigue Dataset for Kirigami Sheet Actuators

**Target venue:** Extreme Mechanics Letters | Smart Materials and Structures  
**Estimated length:** 6 pages  
**Hardware cost:** ~$100

---

**Abstract (draft)**

Kirigami sheet actuators offer flat, low-profile actuation for soft robots, but pattern and material selection remain largely aesthetic or heuristic. We present the first multi-hundred-cycle force-stroke fatigue dataset spanning four cut-pattern families (straight, rotational, spiral, hierarchical) and two material-thickness combinations (Mylar 50μm/125μm, PET 75μm/175μm) — eight conditions, five replicates each, 500 cycles per sample. We show that cut-pattern geometry and material independently predict initial stiffness (η² = [X], [Y]) but interact significantly for fatigue slope (interaction p < 0.05), meaning co-design is required for lifetime-critical applications. We provide a model predicting force-stroke-cycle trade-offs from pattern and material parameters, enabling data-driven actuator selection for the first time.

---

**1. Introduction**

Kirigami — the art of creating 3D structures from 2D sheets via cuts — has been applied to soft actuators [CITE review]. A key unresolved problem is fatigue: how do cut patterns and materials interact to determine actuator lifetime? Khosravi et al. (2021, DOI 10.3389/frobt.2021.749051) measured force-displacement with varied cut geometry but tested only ~5 cycles and one material family. No systematic multi-cycle, multi-pattern, multi-material study exists. We fill this gap.

**2. Experimental Design**

*2.1 Specimens*
Laser-cut on a [machine] from commercial rolls. Four pattern families × 2 materials × 2 thicknesses = 8 conditions × 5 replicates = 40 specimens total. Each specimen: [dimensions].

*2.2 Tensile Cycling Jig*
Custom fixture on a [tensile tester / servo + load cell] rig. Displacement-controlled cycling at [±X mm, freq Hz]. Force and displacement logged at 100 Hz.

*2.3 Measurement Protocol*
Full force-stroke loop recorded at cycles 1, 10, 50, 100, 200, 300, 400, 500. End-of-life defined as >30% peak-force reduction from cycle-1 baseline.

**3. Results (placeholder)**

*3.1 Initial Stiffness*
ANOVA: Pattern F([df])=[F], p=[p]; Material F([df])=[F], p=[p]; Interaction F([df])=[F], p=[p].

*3.2 Fatigue Slope*
[Results showing significant pattern×material interaction]

*3.3 Hysteresis Evolution*
[P-V loop area vs. cycle plots per condition]

**4. Design Model**

Regression model: Stiffness_500 = β₀ + β₁·pattern_code + β₂·material_code + β₃·thickness + β₄·(pattern×material) + ε. R² = [X], RMSE = [Y] N/mm.

**5. Discussion**

Pattern choice and material can be optimized independently for initial stiffness but must be co-designed for fatigue lifetime. Spiral cuts show [best/worst] fatigue resistance. PET outperforms Mylar at [condition]. Hierarchical patterns show non-monotonic fatigue behavior — potential failure mode for designers who extrapolate from early-cycle tests.

**6. Conclusion**

First multi-hundred-cycle, cross-pattern, cross-material fatigue dataset for kirigami actuators. Enables data-driven selection and co-design for lifetime-critical applications.

---

## DRAFT 3 (Rank #4) — F01 (narrowed)
### Which Resistive Tactile Feature Retains Slip-Prediction Lead-Time as Liquid Film Thickness Increases?

**Target venue:** IEEE Sensors Journal | Sensors and Actuators A  
**Estimated length:** 7 pages  
**Hardware cost:** ~$120

---

**Abstract (draft)**

Incipient slip detection under dry and wet conditions is established, but the effect of increasing liquid film thickness on resistive tactile feature lead-time has not been characterized. We fabricate a low-cost (<$50) 4×4 resistive Velostat array and grasp cylinders at five controlled water-film thicknesses (0, 0.25, 0.5, 1.0, 2.0 mm). We characterize five signal features — pressure centroid drift, contact-area rate of change, high-frequency vibration power, contact-area asymmetry, and normal-force derivative — and measure each feature's slip-prediction lead-time and F1-score as a function of film thickness. We find that [feature X] retains the most lead-time across all film conditions while [feature Y] degrades sharply above [threshold] mm film. These results provide the first feature-selection guidance for resistive tactile arrays deployed in wet manipulation environments.

---

**1. Introduction**

Slip detection is essential for robust grasping. Low-cost resistive tactile arrays (Velostat, FSR sheets) offer practical slip sensing without the cost of optical or capacitive systems. On dry surfaces, Romeo et al. (2017, DOI 10.3390/s17081844) characterized resistive incipient slip. In wet environments, Adachi et al. (2026, DOI 10.1038/s41598-026-41096-z) demonstrated slip detection under water and oil using a high-cost AI-integrated e-skin. The "first wet slip detector" contribution is no longer available. What remains open is a controlled ablation: which tactile feature best survives increasing film thickness? Resistive arrays change conductance with absorbed water (an artifact not present in optical sensors), making the feature ranking non-obvious and potentially different from the dry-contact or optical-sensor literature.

**2. Sensor Fabrication**

4×4 Velostat matrix with copper-tape electrodes on FR4 backing. Column scanning at [freq] Hz. [Calibration procedure]. Total BOM cost: <$50.

*2.1 Film Thickness Control*
[Method: controlled water bath, capillary-gap spacer, or precision syringe pump to coat cylinder surface to target thickness. Measured by profilometer / calibrated optical method before each trial.]

**3. Grasp Protocol**

Cylinder grasps at 5 film thicknesses × 200 trials each = 1000 total. High-speed camera (1000 fps) labels slip onset frame. Five features extracted in a sliding window (width [W] ms, stride [S] ms):
1. Centroid drift rate (mm/s in contact-area centroid)
2. dA/dt (contact area rate of change, pixels/s)
3. HF vibration power (bandpass [20–200 Hz], RMS)
4. Contact asymmetry index
5. dF_n/dt (normal force derivative from summed array output)

**4. Results (placeholder)**

Table: Feature | Lead-time 0mm (ms) | Lead-time 0.5mm | Lead-time 2.0mm | F1 @ 2.0mm
Centroid drift | TBD | TBD | TBD | TBD
dA/dt | TBD | TBD | TBD | TBD
HF power | TBD | TBD | TBD | TBD
Asymmetry | TBD | TBD | TBD | TBD
dF_n/dt | TBD | TBD | TBD | TBD

**5. Discussion**

At low film thickness, [X] dominates because [reason]. Above [threshold] mm, water absorption into Velostat changes baseline conductance and degrades [feature Y]. Practical recommendation: use [X] for wet manipulation below [limit] mm; combine [X]+[Z] above that.

**6. Conclusion**

First controlled film-thickness ablation for resistive tactile slip features. Enables principled feature selection for wet-environment grippers at <$50 sensor cost.

---

## DRAFT 4 (Rank #5) — A02 (reframed)
### Switching Latency Floor and Cycle Degradation of Peltier-Assisted LMPA Variable-Stiffness Joints

**Target venue:** IEEE RA-L | Soft Robotics  
**Estimated length:** 7 pages  
**Hardware cost:** ~$250

---

**Abstract (draft)**

Low-melting-point alloy (LMPA) variable-stiffness joints offer high stiffness ratios but are constrained by slow thermal switching. We characterize the switching-speed, stiffness-ratio, and cycle-life trade-surface for Field's-metal-filled silicone joints with Peltier-element active cooling. Resistive heating alone achieves melt in ~50 s; passive solidification requires ~90 s (consistent with Esser et al., RoboSoft 2024). With Peltier assistance, we measure the latency floor across three Peltier power levels and map the resulting latency–stiffness-ratio–cycle-life trade surface over 200 thermal cycles. We find that [result about trade-off]. Cycle-life degradation beyond 80 cycles, noted but not systematically characterized by Al Harthy et al. (2025, DOI 10.1002/aisy.202500756), is quantified and modeled. These results define the physical design space for LMPA joints under application-specific latency requirements.

---

**1. Introduction**

Variable-stiffness joints allow robots to switch between compliant and rigid configurations, enabling safe human interaction during approach and high-force capability during manipulation. LMPAs such as Field's metal (melting point 62°C) are attractive because they achieve stiffness ratios of [X:1] [CITE]. However, thermal switching is slow. Resistive heating takes ~50 s to melt; passive cooling takes ~90 s to solidify [Esser et al., RoboSoft 2024]. Forced convection reduces this to ~28–30 s [Gaira et al. 2025, DOI 10.1002/adrr.202500031]; only the melt direction approaches sub-second with aggressive resistive heating [Schubert & Floreano 2013, DOI 10.1039/c3ra44412k].

Sub-500 ms reactive grasping is not physically achievable under passive cooling. The open design question is different: given that a designer accepts a latency budget (e.g., 30 s, 10 s, 5 s), what stiffness ratio and cycle lifetime can they achieve? And how does the 80-cycle degradation noted by Al Harthy et al. progress? These questions define the design trade surface.

**2. Hardware**

*2.1 Joint Fabrication*
[Dimensions, alloy, silicone shell, heater wire specification, Peltier element selection and mounting.]

*2.2 Characterization Fixture*
Load cell for stiffness measurement (rigid vs. molten state). Thermocouple at alloy core. Peltier current controller. Data logger at 10 Hz.

**3. Protocol**

For each of 3 Peltier power levels (0W / [X]W / [Y]W) × 5 joint prototypes:
- Measure melt latency (time from heater on to >90% stiffness drop, defined as [criterion])
- Measure solidify latency (time from heater off + Peltier on to >90% stiffness recovery)
- Measure stiffness ratio (rigid/molten bending stiffness at [load])
- Repeat for 200 cycles, record each latency and stiffness ratio

**4. Results (placeholder)**

*4.1 Latency Floor*
Table: Peltier Power | Melt Latency (s) | Solidify Latency (s) | Stiffness Ratio | N cycles to 10% degradation

*4.2 Trade Surface*
3D surface plot: x=melt latency, y=solidify latency, z=stiffness ratio, colored by Peltier power.

*4.3 Cycle Degradation*
Latency and stiffness ratio as function of cycle number, per condition. Model: [linear / exponential decay?].

**5. Discussion**

The latency floor under maximum Peltier power is [X] s, enabling applications with [Y]-second reaction requirements. Beyond 80 cycles, [describe degradation pattern]. The latency–stiffness–life trade surface enables principled LMPA joint selection for a given application.

**6. Conclusion**

First characterization of the Peltier-assisted LMPA switching trade surface and post-80-cycle degradation. Provides design guidance replacing the currently heuristic parameter choices in LMPA joint design.

---

## DRAFT 5 (Rank #6) — H01 (high-risk, IPC framing)
### Information Processing Capacity vs. Strut Stiffness in Physical Tensegrity Reservoirs: Does Hardware Match Simulation?

**Target venue:** Advanced Intelligent Systems | Science Robotics (long shot)  
**Estimated length:** 8 pages  
**Hardware cost:** ~$240

---

**Abstract (draft)**

Physical reservoir computing (PRC) in tensegrity robots uses the mechanical body as a nonlinear dynamical reservoir, enabling temporal computation without dedicated controllers. Simulation studies show that strut stiffness ratio sets reservoir memory capacity [Fujita et al. 2018, DOI 10.12792/jiiae.6.92], but this has not been validated in physical hardware. We build three 5-bar tensegrity robots at three strut stiffness ratios and measure Information Processing Capacity (IPC, Dambre et al. 2012, DOI 10.1038/srep00514) — the theoretically correct metric, not Lyapunov exponent — using standard sinusoidal input streams. We test whether (1) the IPC-vs-stiffness trend matches Fujita's simulation prediction, (2) the IPC peak aligns with the echo-state property boundary rather than the edge-of-chaos, and (3) a downstream temporal classification task (payload weight identification from steady-state vibration) confirms the IPC ranking. We find [result]. These results provide the first physical validation of simulation-based tensegrity PRC design rules.

---

**1. Introduction**

Physical reservoir computing exploits a system's own dynamics as a computational reservoir [Nakajima & Fischer 2021]. Caluwaerts et al. (2013, DOI 10.1162/ARTL_a_00080) demonstrated PRC in tensegrity simulation. Recent work showed PRC works in physical tensegrity hardware [AIP Chaos 2025, arXiv:2507.21496; Nature Communications 2026]. However, the mapping from mechanical parameters to reservoir quality has only been characterized in simulation [Fujita et al. 2018]. Two conceptual issues must be addressed in the physical study:

1. **Correct metric:** The right quantity is IPC (Dambre et al., Sci. Reports 2:514, 2012, DOI 10.1038/srep00514), which decomposes memory capacity into linear and nonlinear components. Lyapunov exponent characterizes chaos, not memory capacity — they correlate only approximately.
2. **Correct boundary:** IPC peaks at the echo-state property boundary (spectral radius < 1 for the Jacobian of the reservoir map), not necessarily at edge-of-chaos [Taniguchi 2025, arXiv:2503.12957].

The physical-vs-simulation gap is the unverified claim: do real mechanical imperfections, damping, and fabrication variability shift the IPC peak relative to the simulation curve?

**2. Hardware Design**

*2.1 Tensegrity Structure*
5-bar tensegrity. Struts: carbon fibre rods (modulus fixed). Cables: elastic cord at three pre-tension levels corresponding to stiffness ratios [r1, r2, r3]. Cost per robot: ~$80.

*2.2 Sensing*
Accelerometer (MPU-6050 or similar) at each node. IMU data streamed at [freq] Hz via USB.

*2.3 Input*
Sinusoidal perturbation applied to one node via a servo-driven cable. Input frequency sweep: [range] Hz.

**3. IPC Measurement Protocol**

Following Dambre et al. 2012: apply sine wave input u(t), read state x(t) from all accelerometers, train linear readout to reconstruct [u(t), u²(t), u(t-1), u(t-1)², …] from x(t). IPC = sum of R² across all reconstructed basis functions. Compute for each stiffness-ratio robot across [N_trials] trials.

**4. Echo-State Property Boundary**

Perturb reservoir identically twice from slightly different initial conditions; measure state divergence vs. time. Echo-state property holds when divergence decays. Map boundary in stiffness-ratio space.

**5. Temporal Classification Task**

Attach [M1, M2, M3] kg payload to one node. Classify payload from 500ms of steady-state vibration using linear readout trained on reservoir states. Compare classification accuracy vs. IPC for each stiffness ratio.

**6. Results (placeholder)**

Fig 1: IPC vs. stiffness ratio (physical) overlaid on Fujita 2018 simulation curve.
Fig 2: Echo-state property boundary in stiffness-ratio space.
Fig 3: Classification accuracy vs. IPC.

**7. Discussion**

If physical IPC curve matches simulation: tensegrity PRC design rules transfer from simulation to hardware.
If not: characterize the gap (likely due to cable hysteresis and damping) and propose correction factors.

Limitations: 5-bar structure only, sinusoidal input only, 3 stiffness levels. Future work: larger structures, richer input classes, coupling to locomotion tasks.

**8. Conclusion**

First physical validation of simulation-derived IPC-vs-stiffness design rules for tensegrity PRC. Provides evidence for or against using simulation to pre-select tensegrity mechanical parameters before fabrication.

---

*End of rough drafts. Next steps: (1) run deep-research on remaining 17 outline items, (2) pick one draft for advisor review, (3) begin fabrication planning for chosen topic.*
