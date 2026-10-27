---
title: "Tuning PostgreSQL Knobs with PyTorch"
description: "Notes from our final year project on automating PostgreSQL configuration tuning using workload metrics and a lightweight PyTorch pipeline."
pubDate: 2026-10-18
tags: ["postgresql", "python", "pytorch", "databases"]
draft: false
---

PostgreSQL comes with hundreds of configuration parameters in `postgresql.conf`, and its default values are intentionally conservative so it can run on almost any machine. In practice, getting good performance out of a database usually means manually adjusting parameters like `shared_buffers`, `work_mem`, and `effective_cache_size` based on the workload.

For our Final Year Project at the University of Moratuwa, we have been building a lightweight machine learning pipeline in Python and PyTorch to automate this tuning process based on runtime workload metrics.

## Why Manual Tuning Gets Difficult

Even when focusing on a smaller subset of $k = 12$ memory, checkpoint, and query planner parameters, the parameters interact with each other in non-obvious ways. For example, raising `work_mem` allows larger sorts and hash tables to stay in memory instead of spilling to disk, but setting it too high under heavy concurrency can quickly exhaust system RAM.

We treat configuration tuning as an optimization problem over a given workload $\mathcal{W}$:

$$
\theta^* = \arg\max_{\theta \in \Theta} \; \mathbb{E}_{w \sim \mathcal{W}} \left[ \frac{\text{Throughput}(w, \theta)}{\text{Latency}_{p99}(w, \theta)} \right]
$$

where $\theta \in \Theta$ is the vector of database configuration parameters and $w$ is the set of runtime statistics collected from views like `pg_stat_database` and `pg_stat_bgwriter`.

## Representing Workloads in Python

Instead of parsing raw SQL queries, we represent a workload using storage and execution counters—such as buffer cache hit ratios, sequential vs. index scan ratios, temporary file usage, and checkpoint activity.

```python
from dataclasses import dataclass
import torch
import torch.nn as nn

@dataclass
class WorkloadMetrics:
    blks_read_per_sec: float
    blks_hit_ratio: float
    temp_bytes_spilled: float
    tup_fetched_ratio: float

class KnobRecommender(nn.Module):
    def __init__(self, metric_dim: int = 16, knob_dim: int = 8) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(metric_dim, 64),
            nn.ReLU(),
            nn.LayerNorm(64),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, knob_dim),
            nn.Sigmoid(),  # Normalized [0, 1] range mapped to safe knob bounds
        )

    def forward(self, metrics: torch.Tensor) -> torch.Tensor:
        return self.net(metrics)
```

## Takeaways So Far

1. **Bounding the Search Space**: Clamping recommended values to safe hardware limits (especially memory-related knobs) is essential so an experimental configuration never crashes the database process.
2. **Adapting to Changing Workloads**: Read-heavy analytical queries and write-heavy transactional workloads need very different settings, so keeping the model small and fast to evaluate makes a noticeable difference.
