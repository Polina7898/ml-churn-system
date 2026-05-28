import os
from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from src.data import generate_dataset
from src.features import FEATURE_NAMES, init_feature_store

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "churn_model.pkl"
QUALITY_THRESHOLD_ROC_AUC = 0.80


def log_to_mlflow(params, metrics, model_path):
    uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if not uri.startswith("http"):
        print("MLflow tracking server недоступен, пропускаем логирование")
        return
    try:
        import mlflow
        import mlflow.sklearn
        mlflow.set_tracking_uri(uri)
        mlflow.set_experiment("churn-prediction")
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(model_path))
            print(f"Эксперимент залогирован в MLflow на {uri}")
    except Exception as exc:
        print(f"MLflow логирование пропущено: {exc}")


def train():
    init_feature_store()
    MODEL_DIR.mkdir(exist_ok=True)

    df = generate_dataset()
    x = df[FEATURE_NAMES]
    y = df["churn"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.08,
        "random_state": 42,
    }

    model = GradientBoostingClassifier(**params)
    model.fit(x_train, y_train)

    proba = model.predict_proba(x_test)[:, 1]
    pred = model.predict(x_test)

    metrics = {
        "roc_auc": roc_auc_score(y_test, proba),
        "f1": f1_score(y_test, pred),
        "precision": precision_score(y_test, pred),
        "recall": recall_score(y_test, pred),
    }

    joblib.dump(model, MODEL_PATH)

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    if metrics["roc_auc"] < QUALITY_THRESHOLD_ROC_AUC:
        raise RuntimeError(
            f"ROC-AUC {metrics['roc_auc']:.4f} ниже порога {QUALITY_THRESHOLD_ROC_AUC}"
        )

    log_to_mlflow(params, metrics, MODEL_PATH)
    return metrics


if __name__ == "__main__":
    train()
