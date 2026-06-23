"""Phase D dataset generator — dynamic shared-vs-isolated proprioception traces.

20 actuators x 5 life stages x 2 supply topologies x 2 contact states x 5 reps = 2000 traces.

Each trace is a *dynamic* actuation-band excitation -> shared/isolated pneumatic network
(``sim.network``) -> realized pressures -> fatigue-coupled PCC tip pose (``sim.kinematics``)
-> sensor observables (``sim.sensors``). Per Gate 0 the shared-manifold cross-talk lives in
the dynamics, so a static pressure->pose calibrator is blind to its fatigue drift while a
dynamic (ARX) corrector can recover it — the Phase E hypothesis this dataset is built to test.

The split is by **actuator identity** (train ids vs held-out ids), never by trace, so Phase E
generalization is measured on actuators never seen in training.

Outputs (under ``data/sim/phaseD/``):
  * ``dataset[_smoke].npz``  — stacked arrays (fixed time grid ``t``)
  * ``manifest[_smoke].json`` — seed, parameters, actuator table, split, and a SHA-256 of the npz

Run:
    python -m scripts.phaseD_dataset            # full 2000-trace dataset
    python -m scripts.phaseD_dataset --smoke    # tiny subset for CI / sanity
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

import numpy as np

from sim.fatigue import FatigueParams, degraded_sls, fatigue_state
from sim.kinematics import PCCParams, curvature_from_pressure, pcc_transform
from sim.network import _conductances, simulate_network
from sim.plant import NetworkParams, SLSParams
from sim.sensors import SensorModel, SensorParams

# --- frozen experiment design -------------------------------------------------
GLOBAL_SEED = 20260623
N_ACTUATORS = 20
TRAIN_IDS = list(range(0, 14))          # 14 train / 6 held-out actuators
LIFE_FRACTIONS = [0.10, 0.30, 0.50, 0.70, 0.90]
N_REPS = 5
N_NEIGHBORS = 2                         # gripper = focal + 2 neighbors on the manifold
EXCITE_FREQS = [1.0, 2.0, 3.5]          # actuation band [Hz]
EXCITE_DEPTH = 0.30                     # valve modulation depth (keeps gv > 0)
T_DURATION = 4.0                        # [s]
T_POINTS = 240
OUT_DIR = "data/sim/phaseD"


def build_actuators(n=N_ACTUATORS):
    """Deterministic per-actuator geometry, base SLS wall, and rupture life."""
    acts = []
    for aid in range(n):
        r = np.random.default_rng(1000 + aid)
        pcc = PCCParams(
            length_m=0.08 + 0.06 * r.random(),
            kappa_gain=1.5e-5 + 1.0e-5 * r.random(),
            plane_azimuth_rad=2.0 * np.pi * r.random(),
        )
        sls = SLSParams(
            k1=2.0e10 * (0.9 + 0.2 * r.random()),
            k2=2.0e10 * (0.9 + 0.2 * r.random()),
            tau=0.10 * (0.8 + 0.4 * r.random()),
        )
        rupture = 3000.0 + 1000.0 * r.random()
        acts.append({"pcc": pcc, "sls": sls, "rupture": float(rupture)})
    return acts


def make_drive(gv_nominal, freqs, phases, depth):
    """Per-chamber multisine valve-conductance command: gv_i(t) = gv0_i (1 + depth * s_i(t))."""
    freqs = np.asarray(freqs, dtype=float)
    phases = np.asarray(phases, dtype=float)            # (n, k)

    def gv(tt):
        s = np.sin(2.0 * np.pi * freqs[None, :] * tt + phases).mean(axis=1)
        return gv_nominal * (1.0 + depth * s)

    return gv


def all_commands(t, freqs, phases, depth):
    """Zero-mean valve modulation s_ch(t) for every chamber on the time grid -> (T, n_chambers).

    These commands are all observable (you drive every valve), and the shared-manifold
    cross-talk is a function of them — so they are legitimate proprioception features.
    """
    freqs = np.asarray(freqs, dtype=float)
    phases = np.asarray(phases, dtype=float)                 # (n_chambers, k)
    arg = 2.0 * np.pi * freqs[None, None, :] * t[:, None, None] + phases[None, :, :]
    return depth * np.sin(arg).mean(axis=2)                  # (T, n_chambers)


def tip_positions(kappa_series, phi, length_m):
    """Tip position (T,3) from a curvature time series for a fixed-azimuth PCC segment."""
    out = np.empty((kappa_series.size, 3))
    for i, kappa in enumerate(kappa_series):
        out[i] = pcc_transform(float(kappa), phi, length_m)[:3, 3]
    return out


def generate(smoke=False):
    acts = build_actuators()
    net = NetworkParams(n_chambers=1 + N_NEIGHBORS)
    _, _, gv_nominal = _conductances(net.n_chambers, net, None)
    t = np.linspace(0.0, T_DURATION, T_POINTS)
    fp_base = FatigueParams()

    focal_ids = [0, 1, 19] if smoke else list(range(N_ACTUATORS))
    life_fracs = [0.30, 0.70] if smoke else LIFE_FRACTIONS
    reps = 1 if smoke else N_REPS
    topologies = ["isolated", "shared"]
    contacts = [False, True]

    cols = {k: [] for k in (
        "meas_manifold_pressure", "meas_chamber_pressure", "meas_volume", "cmd_valve",
        "cmd_all", "meas_position", "true_position", "true_kappa", "meas_contact",
        "compliance_mult", "leak_mult", "topology", "contact_state",
        "actuator_id", "life_frac", "rep")}

    for aid in focal_ids:
        focal = acts[aid]
        pcc = focal["pcc"]
        neigh_ids = [(aid + 1 + j) % N_ACTUATORS for j in range(N_NEIGHBORS)]
        fp_focal = FatigueParams(rupture_cycles=focal["rupture"])
        for life in life_fracs:
            fs = fatigue_state(life * focal["rupture"], 0.0, fp_focal)
            # degrade every chamber in the gripper to this life stage
            sls_list = [degraded_sls(acts[i]["sls"], fs) for i in [aid] + neigh_ids]
            leak = np.full(net.n_chambers, fs.leak_multiplier)
            for rep in range(reps):
                phases = np.array([
                    np.random.default_rng([GLOBAL_SEED, aid, rep, ch]).uniform(
                        0.0, 2.0 * np.pi, size=len(EXCITE_FREQS))
                    for ch in range(net.n_chambers)])
                gv = make_drive(gv_nominal, EXCITE_FREQS, phases, EXCITE_DEPTH)
                cmd_all_arr = all_commands(t, EXCITE_FREQS, phases, EXCITE_DEPTH)
                cmd0 = cmd_all_arr[:, 0]
                for topo in topologies:
                    res = simulate_network(t, gv, topo, sls_list, net, leak_multiplier=leak)
                    # observable manifold pressure seen by the focal chamber
                    if topo == "shared":
                        manifold = res["P_m"]
                    else:
                        manifold = res["P_m"][0]
                    chamber_p = res["P"][0]
                    chamber_v = res["V"][0]
                    kappa = curvature_from_pressure(chamber_p, fs.compliance_multiplier, pcc)
                    pos = tip_positions(kappa, pcc.plane_azimuth_rad, pcc.length_m)
                    reach = np.hypot(pos[:, 0], pos[:, 1])
                    for contact in contacts:
                        if contact:
                            d_contact = 0.5 * float(reach.max())
                            penetration = np.clip(reach - d_contact, 0.0, None)
                        else:
                            penetration = np.zeros_like(reach)
                        sm = SensorModel(
                            params=SensorParams(),
                            seed=int(np.random.default_rng(
                                [GLOBAL_SEED, aid, rep, int(topo == "shared"), int(contact)]
                            ).integers(0, 2**31 - 1)))
                        meas = sm.measure(pressure=manifold, volume=chamber_v,
                                          position=pos, penetration=penetration)
                        cols["meas_manifold_pressure"].append(meas["pressure"])
                        cols["meas_chamber_pressure"].append(
                            sm.measure(pressure=chamber_p)["pressure"])
                        cols["meas_volume"].append(meas["volume"])
                        cols["cmd_valve"].append(cmd0)
                        cols["cmd_all"].append(cmd_all_arr)
                        cols["meas_position"].append(meas["position"])
                        cols["true_position"].append(pos)
                        cols["true_kappa"].append(kappa)
                        cols["meas_contact"].append(meas["contact"])
                        cols["compliance_mult"].append(fs.compliance_multiplier)
                        cols["leak_mult"].append(fs.leak_multiplier)
                        cols["topology"].append(1 if topo == "shared" else 0)
                        cols["contact_state"].append(bool(contact))
                        cols["actuator_id"].append(aid)
                        cols["life_frac"].append(life)
                        cols["rep"].append(rep)

    arrays = {
        "t": t,
        "meas_manifold_pressure": np.asarray(cols["meas_manifold_pressure"]),
        "meas_chamber_pressure": np.asarray(cols["meas_chamber_pressure"]),
        "meas_volume": np.asarray(cols["meas_volume"]),
        "cmd_valve": np.asarray(cols["cmd_valve"]),
        "cmd_all": np.asarray(cols["cmd_all"]),
        "meas_position": np.asarray(cols["meas_position"]),
        "true_position": np.asarray(cols["true_position"]),
        "true_kappa": np.asarray(cols["true_kappa"]),
        "meas_contact": np.asarray(cols["meas_contact"]),
        "compliance_mult": np.asarray(cols["compliance_mult"]),
        "leak_mult": np.asarray(cols["leak_mult"]),
        "topology": np.asarray(cols["topology"], dtype=int),
        "contact_state": np.asarray(cols["contact_state"], dtype=bool),
        "actuator_id": np.asarray(cols["actuator_id"], dtype=int),
        "life_frac": np.asarray(cols["life_frac"]),
        "rep": np.asarray(cols["rep"], dtype=int),
    }
    return arrays, acts


def _actuator_table(acts):
    return [{
        "id": i,
        "length_m": a["pcc"].length_m,
        "kappa_gain": a["pcc"].kappa_gain,
        "plane_azimuth_rad": a["pcc"].plane_azimuth_rad,
        "k1": a["sls"].k1, "k2": a["sls"].k2, "tau": a["sls"].tau,
        "rupture_cycles": a["rupture"],
    } for i, a in enumerate(acts)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="tiny subset for CI / sanity")
    parser.add_argument("--out", default=OUT_DIR)
    args = parser.parse_args()

    arrays, acts = generate(smoke=args.smoke)
    os.makedirs(args.out, exist_ok=True)
    tag = "_smoke" if args.smoke else ""
    npz_path = os.path.join(args.out, f"dataset{tag}.npz")
    np.savez_compressed(npz_path, **arrays)
    with open(npz_path, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()

    n_traces = int(arrays["actuator_id"].size)
    test_ids = [i for i in range(N_ACTUATORS) if i not in TRAIN_IDS]
    manifest = {
        "seed": GLOBAL_SEED,
        "smoke": args.smoke,
        "n_traces": n_traces,
        "time": {"duration_s": T_DURATION, "n_points": T_POINTS},
        "excitation": {"freqs_hz": EXCITE_FREQS, "depth": EXCITE_DEPTH},
        "design": {
            "n_actuators": N_ACTUATORS, "n_neighbors": N_NEIGHBORS,
            "life_fractions": LIFE_FRACTIONS, "topologies": ["isolated", "shared"],
            "contact_states": [False, True], "n_reps": N_REPS,
        },
        "split_by_actuator_identity": {"train_ids": TRAIN_IDS, "test_ids": test_ids},
        "actuators": _actuator_table(acts),
        "arrays": {k: list(np.asarray(v).shape) for k, v in arrays.items()},
        "npz_sha256": sha,
        "npz_file": os.path.basename(npz_path),
    }
    manifest_path = os.path.join(args.out, f"manifest{tag}.json")
    with open(manifest_path, "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"wrote {n_traces} traces -> {npz_path}")
    print(f"manifest -> {manifest_path}")
    print(f"sha256 {sha}")
    print(f"train actuators {TRAIN_IDS}")
    print(f"held-out actuators {test_ids}")


if __name__ == "__main__":
    main()
