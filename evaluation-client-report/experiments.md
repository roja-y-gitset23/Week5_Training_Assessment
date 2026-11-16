# Experiment Log

| Config | What changed | Faithfulness | Answer Rel. | Ctx Precision | Ctx Recall |
|---|---|---|---|---|---|
| A | Baseline: 20-word chunks, no overlap, top_k=3 | nan | nan | nan | nan |
| B | 60-word chunks, 15-word overlap, top_k=3 | nan | nan | nan | nan |

**Decision:** Ship Config A. Larger overlapping chunks keep each policy fact whole, so the model sees complete evidence and invents less.
