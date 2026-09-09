"""Developer negative controls: local generated files must not weaken the gate."""

import pytest

import test_figure_manifest as gate


@pytest.mark.parametrize("mutation", ["undeclared_local_input", "missing_generator", "missing_consumer"])
def test_local_file_cannot_bypass_input_provenance(tmp_path, monkeypatch, mutation):
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    (tmp_path / "input.npz").write_bytes(b"synthetic local input, not a dataset")
    entry = {"id": "figure", "inputs": ["input.npz"],
             "command": "python -m scripts.make_input && python -m scripts.figure"}
    manifest = {"figures": [entry], "generated_inputs": {
        "input.npz": {"command": "python -m scripts.make_input", "consumers": ["figure"]}}}
    if mutation == "undeclared_local_input":
        manifest["generated_inputs"] = {}
    elif mutation == "missing_generator":
        entry["command"] = "python -m scripts.figure"
    else:
        manifest["generated_inputs"]["input.npz"]["consumers"] = []
    with pytest.raises(AssertionError):
        gate.test_inputs_are_committed_or_declared_generated(manifest, tracked=set())


@pytest.mark.parametrize("present", [False, True])
def test_declared_generated_input_is_valid_before_and_after_regeneration(tmp_path, monkeypatch, present):
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    if present:
        (tmp_path / "input.npz").write_bytes(b"synthetic local input")
    manifest = {"figures": [{"id": "figure", "inputs": ["input.npz"],
                             "command": "python -m scripts.make_input && python -m scripts.figure"}],
                "generated_inputs": {"input.npz": {
                    "command": "python -m scripts.make_input", "consumers": ["figure"]}}}
    gate.test_inputs_are_committed_or_declared_generated(manifest, tracked=set())


def test_committed_input_must_be_present_but_needs_no_generated_declaration(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    manifest = {"figures": [{"id": "figure", "inputs": ["source.py"]}]}
    tracked = {"source.py"}
    with pytest.raises(AssertionError, match="missing from disk"):
        gate.test_inputs_are_committed_or_declared_generated(manifest, tracked)
    (tmp_path / "source.py").write_text("# synthetic committed-source stand-in\n")
    gate.test_inputs_are_committed_or_declared_generated(manifest, tracked)
