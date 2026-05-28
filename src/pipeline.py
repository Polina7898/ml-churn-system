import shutil
from pathlib import Path

import joblib
from prefect import flow, get_run_logger, task
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from src.data import generate_dataset
from src.features import FEATURE_NAMES, init_feature_store
from src.train import MODEL_PATH, QUALITY_THRESHOLD_ROC_AUC, train

DEPLOY_PATH = Path("models/churn_model_prod.pkl")


@task(name="prepare-features")
def prepare_features():
    init_feature_store()


@task(name="extract-data")
def extract_data():
    return generate_dataset()


@task(name="train-model")
def train_model():
    return train()


@task(name="validate-model")
def validate_model(metrics: dict):
    logger = get_run_logger()
    if metrics["roc_auc"] < QUALITY_THRESHOLD_ROC_AUC:
        logger.error(f"ROC-AUC {metrics['roc_auc']:.4f} ниже порога")
        raise RuntimeError("Model validation failed")
    logger.info(f"Validation passed: ROC-AUC = {metrics['roc_auc']:.4f}")


@task(name="promote-model")
def promote_model():
    shutil.copy(MODEL_PATH, DEPLOY_PATH)
    return DEPLOY_PATH


@task(name="shadow-test")
def shadow_test(model_path: Path):
    df = generate_dataset(n_rows=500, seed=99)
    x = df[FEATURE_NAMES]
    y = df["churn"]
    model = joblib.load(model_path)
    auc = roc_auc_score(y, model.predict_proba(x)[:, 1])
    if auc < QUALITY_THRESHOLD_ROC_AUC - 0.05:
        raise RuntimeError(f"Shadow test failed: AUC = {auc:.4f}")
    return auc


@flow(name="churn-training-pipeline")
def training_pipeline():
    prepare_features()
    extract_data()
    metrics = train_model()
    validate_model(metrics)
    model_path = promote_model()
    shadow_test(model_path)


if __name__ == "__main__":
    training_pipeline()
