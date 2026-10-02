"""Small deterministic checks; no course data, downloads or training jobs."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    spec = importlib.util.spec_from_file_location(relative.replace("/", "_"), ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("p", [1, 2, 3])
def test_knn_matches_minkowski_reference(p):
    from sklearn.neighbors import KNeighborsClassifier

    cls = load("machine-learning/supervised-learning/knn/HW1.py").KnnClassifier
    rng = np.random.default_rng(71)
    x, q = rng.normal(size=(15, 4)), rng.normal(size=(20, 4))
    y = np.arange(15, dtype=np.uint8) % 2
    model = cls(3, p)
    model.fit(x, y)
    # No distance or voting ties in this case: compare independent implementation.
    np.testing.assert_array_equal(model.predict(q), KNeighborsClassifier(3, p=p).fit(x, y).predict(q))


def test_knn_full_training_set_and_deterministic_tie():
    cls = load("machine-learning/supervised-learning/knn/HW1.py").KnnClassifier
    model = cls(2, 1)
    model.fit(np.array([[-1.], [1.]]), np.array([2, 1], dtype=np.uint8))
    assert model.predict(np.array([[0.]]))[0] == 1
    model.k = 3
    with pytest.raises(ValueError):
        model.predict(np.array([[0.]]))


def test_knn_vote_tie_does_not_choose_a_minority_class():
    cls = load("machine-learning/supervised-learning/knn/HW1.py").KnnClassifier
    model = cls(5, 2)
    model.fit(np.arange(1, 6).reshape(-1, 1), np.array([0, 1, 2, 1, 2], dtype=np.uint8))
    assert model.predict(np.array([[0.]]))[0] == 1


def test_perceptron_terminates_on_inseparable_data():
    cls = load("machine-learning/supervised-learning/perceptron/HW2_wet.py").PerceptronClassifier
    model = cls(max_epochs=5)
    assert model.fit(np.ones((2, 1)), np.array([0, 1])) is False
    assert model.n_epochs_ == 5
    assert not model.converged_


def test_perceptron_learns_separable_data():
    cls = load("machine-learning/supervised-learning/perceptron/HW2_wet.py").PerceptronClassifier
    x = np.array([[-2.], [-1.], [1.], [2.]])
    y = np.array([0, 0, 1, 1])
    model = cls()
    assert model.fit(x, y) is True
    assert model.converged_
    np.testing.assert_array_equal(model.predict(x), y)


@pytest.mark.parametrize("activation", ["sigmoid", "tanh"])
def test_manual_mlp_gradient_matches_autograd(activation):
    import torch

    m = load("deep-learning/neural-network-fundamentals/manual-mlp/model.py")
    torch.manual_seed(8)
    net = m.FullyConnectedNetwork(3, 2, 4, getattr(m, activation), lr=0.1)
    x = torch.randn(5, 3)
    y = torch.tensor([0, 1, 1, 0, 1])
    original = [a.clone() for a in (net.W1, net.b1, net.W2, net.b2)]
    w1, b1, w2, b2 = [a.clone().requires_grad_() for a in original]
    logits = getattr(torch, activation)(x @ w1 + b1) @ w2 + b2
    torch.nn.functional.cross_entropy(logits, y).backward()
    net.backward(x, y, net.forward(x))
    for old, new, reference in zip(original, (net.W1, net.b1, net.W2, net.b2), (w1, b1, w2, b2)):
        torch.testing.assert_close((old - new) / net.lr, reference.grad, atol=2e-6, rtol=2e-5)


def test_manual_mlp_rejects_unknown_activation():
    m = load("deep-learning/neural-network-fundamentals/manual-mlp/model.py")
    with pytest.raises(ValueError, match="Hidden activation"):
        m.FullyConnectedNetwork(3, 2, 4, lambda x: x)


def test_manual_tanh_is_finite_at_large_magnitudes():
    import torch

    m = load("deep-learning/neural-network-fundamentals/manual-mlp/model.py")
    x = torch.tensor([-1000., 0., 1000.])
    torch.testing.assert_close(m.tanh(x), torch.tanh(x))
    torch.testing.assert_close(m.d_tanh(x), torch.tensor([0., 1., 0.]))


def test_perceptron_refit_resets_convergence_state():
    cls = load("machine-learning/supervised-learning/perceptron/HW2_wet.py").PerceptronClassifier
    model = cls(max_epochs=5)
    assert model.fit(np.array([[-1.], [1.]]), np.array([0, 1])) is True
    assert model.fit(np.ones((2, 1)), np.array([0, 1])) is False
    assert not model.converged_
    assert model.n_epochs_ == 5


def test_cat_cnn_forward_shape():
    import torch

    m = load("deep-learning/neural-network-fundamentals/cat-classification-cnn/model.py")
    net = m.CompactCatCNN_v2(num_classes=3).eval()
    with torch.no_grad():
        assert tuple(net(torch.zeros(2, 3, 32, 32)).shape) == (2, 3)


def test_influence_experiment_references_exist():
    import ast

    base = ROOT / "ai-and-decision-making/recommendation-and-auctions/influence-maximization"
    module = load(str((base / "influence_maximization.py").relative_to(ROOT)))
    for name in ["campaign_experiments.py", "optimize_shield.py"]:
        tree = ast.parse((base / name).read_text(encoding="utf-8"))
        refs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
                and isinstance(n.value, ast.Name) and n.value.id == "cs"}
        assert all(hasattr(module, attr) for attr in refs)


def test_vector_index_after_delete_and_reinsert():
    cls = load("information-retrieval/fundamentals/vector-index/vector_index.py").VectorIndex
    idx = cls(2)
    idx.insert({1: np.array([1., 0.]), 2: np.array([0., 1.]), 3: np.array([2., 0.])})
    idx.delete(np.array([1]))
    idx.insert({4: np.array([3., 0.])})
    assert idx.search(np.array([[1., 0.]]), 2).tolist() == [[4, 3]]
    idx.delete(np.array([2, 3, 4]))
    assert idx.search(np.array([[1., 0.]]), 5).shape == (1, 0)


def test_influence_deterministic_cascade():
    import networkx as nx

    module = load("ai-and-decision-making/recommendation-and-auctions/influence-maximization/influence_maximization.py")
    graph = nx.path_graph(3)
    p = {i: {"p_plus": 1., "p_minus": 0., "a_plus": 1., "a_minus": 0.} for i in graph}
    assert module.simulate_influence(graph, [0], p, rounds=3) == 3
    assert module.simulate_influence(graph, [], p, rounds=3) == 0


def test_vae_forward_shape():
    import torch

    module = load("deep-learning/flower-vae/hw4_code.py")
    model = module.VAE(latent_dim=8).eval()
    with torch.no_grad():
        output, mu, logvar = model(torch.zeros(2, 3, 128, 128))
    assert tuple(output.shape) == (2, 3, 128, 128)
    assert tuple(mu.shape) == tuple(logvar.shape) == (2, 8)


def test_fgsm_respects_normalized_bounds_and_budget():
    import torch

    m = load("deep-learning/adversarial-and-contrastive-learning/attacks.py")
    mean = torch.tensor(m.SVHN_MEAN).reshape(1, 3, 1, 1)
    std = torch.tensor(m.SVHN_STD).reshape(1, 3, 1, 1)
    raw = torch.tensor([0., .5, 1.]).reshape(1, 1, 1, 3).expand(2, 3, 2, 3)
    x = (raw - mean) / std
    grad = torch.tensor([-1., 1., 1.]).reshape(1, 1, 1, 3).expand_as(x)
    adv = m.fgsm_attack(x, .2, grad)
    recovered = adv * std + mean
    assert recovered.min() >= -1e-7 and recovered.max() <= 1 + 1e-7
    assert (adv - x).abs().max() <= .2 + 1e-6
    torch.testing.assert_close(m.fgsm_attack(x, 0., grad), x)
    torch.testing.assert_close(m.fgsm_attack(x, .2, grad, clamp=False), x + .2 * grad.sign())


@pytest.mark.parametrize("epsilon", [-.1, float("nan")])
def test_fgsm_rejects_invalid_budget(epsilon):
    import torch

    m = load("deep-learning/adversarial-and-contrastive-learning/attacks.py")
    with pytest.raises(ValueError, match="epsilon"):
        m.fgsm_attack(torch.zeros(1, 3, 2, 2), epsilon, torch.ones(1, 3, 2, 2))


def test_entity_matching_data_directory_from_environment(tmp_path, monkeypatch):
    import pickle
    import pandas as pd

    monkeypatch.setenv("ENTITY_MATCHING_DATA_DIR", str(tmp_path))
    for name, identifier in [("tableA.csv", 1), ("tableB.csv", 2)]:
        pd.DataFrame({"id": [identifier], "title": ["Example!"], "manufacturer": ["Acme"]}).to_csv(tmp_path / name, index=False)
    # This pickle is created by this test; no external pickle is loaded.
    (tmp_path / "100_matches.pkl").write_bytes(pickle.dumps([(1, 2)]))
    m = load("machine-learning/entity-matching/em_core.py")
    a, b, known = m.load_tables()
    assert a.iloc[0]["text"] == "example acme"
    assert b.iloc[0]["id"] == 2 and known == {(1, 2)}


def test_influence_eda_import_and_references():
    import ast
    import json

    folder = ROOT / "ai-and-decision-making/recommendation-and-auctions/influence-maximization"
    m = load(str((folder / "influence_maximization.py").relative_to(ROOT)))
    doc = json.loads((folder / "eda.ipynb").read_text(encoding="utf-8"))
    nodes = [n for c in doc["cells"] if c["cell_type"] == "code"
             for n in ast.walk(ast.parse("".join(c["source"])))]
    imports = [n.name for node in nodes if isinstance(node, ast.Import) for n in node.names if n.asname == "cs"]
    assert imports == ["influence_maximization"]
    refs = {n.attr for n in nodes if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "cs"}
    assert all(hasattr(m, name) for name in refs)


def test_active_learning_experiment_script_import_path(tmp_path):
    import shutil
    import subprocess
    import sys

    project = tmp_path / "active-learning"
    (project / "experiments").mkdir(parents=True)
    for rel in ["utils.py", "experiments/experiment_lab.py"]:
        shutil.copyfile(ROOT / "machine-learning/active-learning" / rel, project / rel)
    # Minimal synthetic config for import/--help only; no oracle or data evaluation.
    (project / "constants.yaml").write_text("max_labeled: 5\nmax_runtime_sec: 1\nseeds: [1]\n")
    result = subprocess.run([sys.executable, str(project / "experiments/experiment_lab.py"), "--help"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
