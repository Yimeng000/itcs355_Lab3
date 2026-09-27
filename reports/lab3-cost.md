# Lab 3 Cost per 1,000 Predictions

## Serving configuration

Provider: GCP

Instance: n1-standard-2

Hourly rate used: 3.80 THB/hour

Measured throughput from the Lab 3 load test at concurrency 10:

23.90 requests/second

## Cost per 1,000 predictions

The serving cost is estimated from the instance hourly rate, measured throughput, and assumed utilisation.

| Utilisation | Cost per 1,000 predictions |
|---|---:|
| 5% | 0.8833 THB |
| 25% | 0.1767 THB |
| 80% | 0.0552 THB |

The utilisation assumption is important because the endpoint is charged while it is provisioned, even when it is mostly idle. Therefore lower utilisation produces a higher cost per 1,000 predictions.

For this report, 25% utilisation is used as a representative assumption, giving an estimated serving cost of 0.1767 THB per 1,000 predictions.

## Batch inference breakeven

Following the course cost scaffold, the estimated batch job cost is assumed to be half an hour of the same instance:

3.80 THB/hour × 0.5 hour = 1.90 THB per batch job.

The resulting breakeven is approximately:

0.001034 requests/second, or about 89.3 requests/day.

Below roughly 89 requests per day, scheduled batch inference would be cheaper than keeping the endpoint warm.

Above this request volume, keeping the online endpoint available becomes more reasonable under this course cost model.
