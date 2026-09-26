from concurrent.futures import ThreadPoolExecutor, as_completed

from sklearn.metrics import roc_auc_score, average_precision_score

from cloudlayer.factory import get_adapter
from src import config, data, seeds


ENDPOINT = (
    "projects/259177885839/locations/asia-southeast1/"
    "endpoints/3250835869891821568"
)

MAX_WORKERS = 20


def main():
    cfg = config.load()
    adapter = get_adapter(cfg)

    df = data.load_raw(cfg.raw_path)
    _, _, test_df = data.split(df, seed=seeds.set_all(20260103))

    rows = []

    for _, row in test_df.iterrows():
        payload = {
            feature: float(row[feature])
            for feature in data.FEATURES
        }

        rows.append(
            (
                payload,
                int(row[data.TARGET]),
            )
        )

    y_true = [None] * len(rows)
    y_prob = [None] * len(rows)

    def send_one(index, payload):
        result = adapter.invoke(ENDPOINT, payload)

        # Intentionally use probability only.
        # Do NOT inspect model_version.
        return index, float(result["probability"])

    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(send_one, i, payload): i
            for i, (payload, _) in enumerate(rows)
        }

        for future in as_completed(futures):
            index, probability = future.result()

            y_true[index] = rows[index][1]
            y_prob[index] = probability

            completed += 1
            if completed % 100 == 0:
                print(f"completed {completed}/{len(rows)}")

    roc_auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)

    print()
    print(f"ROC_AUC={roc_auc:.6f}")
    print(f"PR_AUC={pr_auc:.6f}")


if __name__ == "__main__":
    main()
