# Experiment Log

| Config | What changed | Faithfulness | Answer Rel. | Ctx Precision | Ctx Recall |
|---|---|---|---|---|---|
| A | Baseline: 20-word chunks, no overlap, top_k=3 | 0.80 | 0.65 | 0.73 | 0.80 |
| B | 60-word chunks, 15-word overlap, top_k=3 | 0.80 | 0.65 | 0.77 | 0.80 |

**Decision:** Ship Config B. Larger overlapping chunks keep each policy fact whole, so the model sees complete evidence and invents less.
