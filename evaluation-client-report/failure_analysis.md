# Failure Analysis (3 worst questions, Config A)

| Question | Faith. | Ctx Prec. | Ctx Recall | Failure type |
|---|---|---|---|---|
| What is the dress code for client meetings? | 0.00 | 0.00 | 0.00 | Retrieval |
| What is the stock option vesting schedule? | 0.00 | 0.00 | 0.00 | Retrieval |
| How many work-from-home days are allowed per week? | 0.00 | 0.00 | 0.00 | Retrieval |

**Fixed:** What is the dress code for client meetings?

Retrieval fix: re-chunked with 60-word chunks + 15-word overlap (Config B retriever).

| | Faith. | Ctx Prec. | Ctx Recall |
|---|---|---|---|
| Before | 0.00 | 0.00 | 0.00 |
| After | 0.00 | 0.00 | 0.00 |
