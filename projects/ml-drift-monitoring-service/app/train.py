import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"
BASELINE_PATH = BASE_DIR / "baseline.json"


def featurize(texts: list[str]) -> np.ndarray:
    feats = []
    keywords = ["error", "timeout", "latency", "deploy", "database", "login", "billing", "permission"]
    for t in texts:
        s = t.lower()
        length = len(s)
        digits = sum(ch.isdigit() for ch in s)
        kw_counts = [s.count(k) for k in keywords]
        feats.append([length, digits, *kw_counts])
    return np.array(feats, dtype=np.float64)


def make_synthetic(n: int = 5000, seed: int = 7):
    rng = np.random.default_rng(seed)
    labels = []
    texts = []
    for _ in range(n):
        kind = rng.choice(["incident", "request", "access"], p=[0.4, 0.35, 0.25])
        if kind == "incident":
            t = rng.choice(
                [
                    "Error rate increased after deploy",
                    "Timeouts observed in payment service",
                    "High latency reported by users",
                    "Database connection errors",
                ]
            )
            labels.append(1)
        elif kind == "access":
            t = rng.choice(
                [
                    "Login permission denied for user",
                    "Need access to repository",
                    "Role request for production read",
                    "Permission issue in admin panel",
                ]
            )
            labels.append(0)
        else:
            t = rng.choice(
                [
                    "Billing question for last invoice",
                    "Feature request for dashboard",
                    "How to configure notification settings",
                    "Request to update documentation",
                ]
            )
            labels.append(0)

        noise = " ".join(rng.choice(["", "", "", "please", "urgent", "prod", "staging"], size=rng.integers(0, 4)))
        texts.append((t + " " + noise).strip())

    return texts, np.array(labels, dtype=np.int64)


def baseline_from_features(X: np.ndarray) -> dict:
    baseline = {"features": []}
    for i in range(X.shape[1]):
        col = X[:, i]
        hist, edges = np.histogram(col, bins=20)
        baseline["features"].append(
            {
                "bins": edges.tolist(),
                "counts": hist.astype(int).tolist(),
            }
        )
    return baseline


def main() -> None:
    texts, y = make_synthetic()
    X = featurize(texts)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    acc = float(model.score(X_test, y_test))
    joblib.dump({"model": model}, MODEL_PATH)

    baseline = baseline_from_features(X_train)
    baseline["meta"] = {"accuracy": acc, "n_train": int(X_train.shape[0])}
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")

    print(f"saved_model={MODEL_PATH}")
    print(f"saved_baseline={BASELINE_PATH}")
    print(f"test_accuracy={acc:.4f}")


if __name__ == "__main__":
    main()
