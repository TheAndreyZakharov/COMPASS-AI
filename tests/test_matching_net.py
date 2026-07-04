from __future__ import annotations

import torch

from src.models.matching_net import MatchingNetConfig, TaskEmployeeMatchingNet


def test_matching_net_forward_shapes() -> None:
    config = MatchingNetConfig(
        task_input_dim=404,
        employee_input_dim=60,
        pair_input_dim=13,
        task_embedding_dim=32,
        employee_embedding_dim=32,
        hidden_dim=64,
        dropout=0.0,
    )

    model = TaskEmployeeMatchingNet(config)

    batch_size = 8
    task_features = torch.randn(batch_size, config.task_input_dim)
    employee_features = torch.randn(batch_size, config.employee_input_dim)
    pair_features = torch.randn(batch_size, config.pair_input_dim)

    output = model(task_features, employee_features, pair_features)

    assert output["logits"].shape == (batch_size, 1)
    assert output["success_probability"].shape == (batch_size, 1)
    assert output["task_embedding"].shape == (batch_size, config.task_embedding_dim)
    assert output["employee_embedding"].shape == (batch_size, config.employee_embedding_dim)


def test_matching_net_probability_range() -> None:
    config = MatchingNetConfig(
        task_input_dim=10,
        employee_input_dim=8,
        pair_input_dim=4,
        task_embedding_dim=16,
        employee_embedding_dim=16,
        hidden_dim=32,
        dropout=0.0,
    )

    model = TaskEmployeeMatchingNet(config)

    output = model(
        torch.randn(5, 10),
        torch.randn(5, 8),
        torch.randn(5, 4),
    )

    probabilities = output["success_probability"]

    assert torch.all(probabilities >= 0.0)
    assert torch.all(probabilities <= 1.0)


def test_matching_net_backward_step() -> None:
    config = MatchingNetConfig(
        task_input_dim=10,
        employee_input_dim=8,
        pair_input_dim=4,
        task_embedding_dim=16,
        employee_embedding_dim=16,
        hidden_dim=32,
        dropout=0.0,
    )

    model = TaskEmployeeMatchingNet(config)
    criterion = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)

    labels = torch.tensor([[1.0], [0.0], [1.0], [0.0]])

    output = model(
        torch.randn(4, 10),
        torch.randn(4, 8),
        torch.randn(4, 4),
    )

    loss = criterion(output["logits"], labels)
    loss.backward()
    optimizer.step()

    assert loss.item() > 0