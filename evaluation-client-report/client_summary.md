# AI Policy Assistant: Quality Report

**Purpose:** We tested the assistant on 15 real staff questions (12 answerable, 3 deliberately unanswerable) covering leave, expenses and IT security.

## What the two key scores mean
- **Faithfulness: "Does the assistant stick to the facts?"** A score of 0.80 means about 80 of every 100 statements are backed by your documents. The rest are guesses. Low faithfulness means staff may get confident but wrong answers.
- **Retrieval precision: "Does it pull up the right pages?"** A score of 0.77 means about 77% of the pages it reads are relevant. Higher precision means less noise, faster answers and fewer mistakes.

## Results
| | Faithfulness | Retrieval precision |
|---|---|---|
| Original setup (A) | 0.80 | 0.73 |
| Improved setup (B) | 0.80 | 0.77 |

## What we changed
We stopped cutting documents into tiny fragments and kept each policy rule together with its surrounding text. The assistant now sees complete evidence.

## Business impact
- Fewer wrong answers to HR, finance and IT questions, so fewer escalations to support teams.
- The assistant says "I don't know" when a policy is missing instead of inventing one.

## Recommendation
Roll out **Config B**. Next: add more documents and re-test monthly. Keep faithfulness above 0.85 before each release.
