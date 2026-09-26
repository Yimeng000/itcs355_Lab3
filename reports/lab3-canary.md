# Lab 3 Canary Deployment and Rollback

## Setup

A deliberately slightly worse model was trained and registered as version 2.

Baseline model metrics:

- ROC-AUC: 0.838401
- PR-AUC: 0.442749

Worse model metrics:

- ROC-AUC: 0.829368
- PR-AUC: 0.408482

The production endpoint initially served version 1 at 100%.

## Canary deployment

At 2026-09-26T22:41:08+07:00, traffic was changed to:

- version 1: 90%
- version 2: 10%

The deployed model IDs were:

- v1: 8151649465959186432
- v2: 360422110608228352

## Degradation detection

Detection was performed using the 1,200-row held-out test set.

The detection script intentionally used only returned probabilities and ground-truth labels. It did not inspect the model version when deciding whether degradation occurred.

Observed 90/10 canary metrics:

- ROC-AUC: 0.838301
- PR-AUC: 0.434281

Compared with the baseline, ROC-AUC changed only slightly, while PR-AUC decreased from 0.442749 to 0.434281. Therefore PR-AUC was the more useful degradation signal in this experiment.

Detection started at 2026-09-26T23:11:12+07:00 and completed at 2026-09-26T23:30:17+07:00.

Detection time: 19 minutes 5 seconds.

## Rollback

At 2026-09-26T23:31:18+07:00, traffic was rolled back to:

- version 1: 100%
- version 2: 0%

The canary deployment was then undeployed.

At 2026-09-26T23:39:15+07:00, the endpoint contained only version 1 with 100% traffic.

## Required discussion

1. The main degradation metric was PR-AUC because it decreased more clearly than ROC-AUC.
2. Detection took 19 minutes 5 seconds using 1,200 held-out requests.
3. Detection could be faster with parallel requests, smaller evaluation windows, or automated metric thresholds.
4. A 50/50 traffic split would expose more requests to the worse model, so aggregate degradation would likely become easier to detect, but it would also increase user exposure to the worse version.
5. The rollback restored version 1 to 100% traffic and removed the canary deployment.
