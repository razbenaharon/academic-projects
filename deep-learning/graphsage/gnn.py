"""
Student implementation file — implement all TODO sections below.

This is the only Section B file you should submit.
"""

from __future__ import annotations

import numpy as np
import torch
from torch_geometric.nn import SAGEConv


def get_feature_vectors(nodes_df):
    """
    Convert the feature vectors stored in nodes_df["features"] into a
    float tensor of shape [num_nodes, num_features].

    In the supplied Cora data, every feature vector is stored as a string:
    "[0, 1, 0, ..., 0]".
    """
    if "features" not in nodes_df.columns:
        raise ValueError("nodes_df must contain a 'features' column")

    feature_vectors = []

    for raw_features in nodes_df["features"]:
        feature_string = str(raw_features).strip()

        if feature_string.startswith("[") and feature_string.endswith("]"):
            feature_string = feature_string[1:-1]

        vector = np.fromstring(
            feature_string,
            dtype=np.float32,
            sep=",",
        )

        feature_vectors.append(vector)

    if not feature_vectors:
        raise ValueError("No feature vectors were found in nodes_df")

    expected_dimension = len(feature_vectors[0])

    for vector in feature_vectors:
        if len(vector) != expected_dimension:
            raise ValueError(
                "All nodes must have feature vectors of the same length"
            )

    features_array = np.stack(feature_vectors)

    return torch.tensor(features_array, dtype=torch.float)


def get_edges(edges_df, inverse_node_id_mapping):
    """
    Convert citation edges from original node IDs to internal node indices.

    Citation edges are made bidirectional so that information can flow in both
    directions during GraphSAGE message passing.
    """
    required_columns = {"sourceNodeId", "targetNodeId"}

    if not required_columns.issubset(edges_df.columns):
        raise ValueError(
            "edges_df must contain 'sourceNodeId' and 'targetNodeId' columns"
        )

    sources = []
    targets = []

    for source_id, target_id in zip(
        edges_df["sourceNodeId"],
        edges_df["targetNodeId"],
    ):
        if source_id not in inverse_node_id_mapping:
            continue

        if target_id not in inverse_node_id_mapping:
            continue

        source_index = inverse_node_id_mapping[source_id]
        target_index = inverse_node_id_mapping[target_id]

        # Original citation direction.
        sources.append(source_index)
        targets.append(target_index)

        # Reverse direction for bidirectional message passing.
        if source_index != target_index:
            sources.append(target_index)
            targets.append(source_index)

    edge_index = torch.tensor(
        [sources, targets],
        dtype=torch.long,
    )

    # Remove duplicate edges while preserving the required [2, num_edges] shape.
    edge_index = torch.unique(edge_index, dim=1)

    return edge_index


def get_labels(nodes_df, subject_mapping):
    """
    Map each node's subject name to its integer class label.
    """
    if "subject" not in nodes_df.columns:
        raise ValueError("nodes_df must contain a 'subject' column")

    labels = []

    for subject in nodes_df["subject"]:
        if subject not in subject_mapping:
            raise KeyError(f"Unknown subject: {subject}")

        labels.append(subject_mapping[subject])

    return torch.tensor(labels, dtype=torch.long)


class GraphSAGE(torch.nn.Module):
    def __init__(self, hidden_channels, output_dim, seed):
        super().__init__()

        torch.manual_seed(seed)

        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)

        hidden_dim = 256

        self.conv1 = SAGEConv(
            hidden_channels,
            hidden_dim,
            aggr="mean",
        )

        self.conv2 = SAGEConv(
            hidden_dim,
            output_dim,
            aggr="mean",
        )

        self.dropout = 0.6

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = torch.relu(x)

        x = torch.nn.functional.dropout(
            x,
            p=self.dropout,
            training=self.training,
        )

        return self.conv2(x, edge_index)


def train(data, model, optimizer, epochs, evaluate_fn):
    """
    Train the model for the requested number of epochs.

    Training loss is calculated only on data.train_mask.

    Validation accuracy is calculated using:
        evaluate_fn(model, data, data.valid_mask)

    The model with the highest validation accuracy is saved as:
        best_model.pt
    """
    criterion = torch.nn.CrossEntropyLoss()
    best_validation_accuracy = -1.0

    for _ in range(epochs):
        model.train()
        optimizer.zero_grad()

        logits = model(
            data.x,
            data.edge_index,
        )

        loss = criterion(
            logits[data.train_mask],
            data.y[data.train_mask],
        )

        loss.backward()
        optimizer.step()

        validation_accuracy = evaluate_fn(
            model,
            data,
            data.valid_mask,
        )

        if validation_accuracy > best_validation_accuracy:
            best_validation_accuracy = validation_accuracy
            torch.save(model, "best_model.pt")