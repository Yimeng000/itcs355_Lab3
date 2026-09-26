# Lab 3 Load Test Report

## Test setup

Load testing was performed using k6 against the deployed Vertex AI endpoint.

- Region: `asia-southeast1`
- Instance type: `n1-standard-2`
- Replica count: 1
- Test duration: 60 seconds per run
- Concurrency levels: 1, 10, 50
- Predefined latency target: p95 < 500 ms
- Error-rate target: < 1%

## Results

| Concurrency | Requests | Throughput (req/s) | p50 (ms) | p95 (ms) | p99 (ms) | Error rate |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 430 | 7.17 | 130.09 | 229.97 | 269.75 | 0.00% |
| 10 | 1443 | 23.90 | 263.81 | 1033.92 | 4066.19 | 0.00% |
| 50 | 1497 | 24.55 | 1926.55 | 3003.07 | 8388.06 | 0.00% |

## Analysis

At concurrency 1, the service met the predefined p95 latency target of 500 ms.

At concurrency 10, p95 latency increased to approximately 1.03 seconds, exceeding the target. The error rate remained 0%.

At concurrency 50, throughput increased only slightly from 23.90 req/s to 24.55 req/s, while latency increased significantly. The median latency reached approximately 1.93 seconds, p95 reached approximately 3.00 seconds, and p99 reached approximately 8.39 seconds.

This indicates that the single `n1-standard-2` serving instance is close to saturation at higher concurrency levels.

## Breaking point

The first tested concurrency level that failed the predefined p95 target was concurrency 10.

The system shows clear saturation by concurrency 50 because throughput remains around 24 requests per second while latency increases substantially.

## Possible improvements

Possible improvements include:

- increasing the serving instance size;
- increasing the number of replicas;
- using request batching where appropriate;
- reducing model or preprocessing overhead.

No request failures were observed during the three load tests.

## Batch size experiment

I compared 100 individual `/predict` requests with one `/predict/batch`
request containing 100 rows.

- 100 individual requests: 20.4025 s total
- One 100-row batch request: 0.2422 s total
- Average time per row in the batch: 2.42 ms
- Batch speedup: approximately 84.2x
- Total time reduction: approximately 98.8%

For this model and service, batching is substantially more efficient because
HTTP and request-processing overhead is paid once for 100 rows instead of once
per prediction.

## Payload size experiment

I increased the HTTP request size while keeping the actual model input unchanged.
Extra JSON whitespace was appended so the request remained valid and produced the same prediction.

| Payload size | Median latency | p95 latency |
|---|---:|---:|
| 137 B | 405.24 ms | 515.66 ms |
| 10 KB | 423.16 ms | 503.14 ms |
| 100 KB | 457.57 ms | 515.63 ms |
| 1 MB | 804.48 ms | 861.86 ms |

Payload size had little effect at 10 KB and only a moderate effect at 100 KB.
At approximately 1 MB, latency increased substantially, with median latency rising from about
405 ms to 804 ms.

This suggests that request serialization, transfer, and parsing overhead become significant
at around the 1 MB payload range for this deployment.

## Instance size experiment

I compared the original `n1-standard-2` instance with one step up,
`n1-standard-4`, using the same workload: 10 VUs for 60 seconds.

| Instance | Throughput (req/s) | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | Hourly cost |
|---|---:|---:|---:|---:|---:|---:|
| n1-standard-2 | 23.90 | 263.81 | 1033.92 | 4066.19 | 0.00% | 3.8 THB/h |
| n1-standard-4 | 27.18 | 253.44 | 445.73 | 3443.59 | 0.00% | 7.6 THB/h |

Moving from `n1-standard-2` to `n1-standard-4` increased throughput by approximately 13.7%.

The p95 latency improved from 1033.92 ms to 445.73 ms, which is an improvement of approximately 56.9%. The larger instance therefore met the predefined p95 target of 500 ms at concurrency 10.

The hourly compute cost increased from approximately 3.8 THB/hour to 7.6 THB/hour, which is a 100% increase.

For this workload, the larger instance substantially improves tail latency, but the cost doubles while throughput improves by only about 13.7%.