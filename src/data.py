import numpy as np
import pandas as pd

from src.features import FEATURE_NAMES


def generate_dataset(n_rows: int = 7043, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(0, 72, n_rows)
    monthly_charges = rng.uniform(18, 120, n_rows)
    total_charges = tenure * monthly_charges + rng.normal(0, 50, n_rows)
    total_charges = np.clip(total_charges, 0, None)
    contract = rng.choice([0, 1, 2], n_rows, p=[0.55, 0.21, 0.24])
    internet_service = rng.choice([0, 1, 2], n_rows, p=[0.34, 0.44, 0.22])
    payment_method = rng.choice([0, 1, 2, 3], n_rows)

    logit = (
        -0.5
        + 0.06 * (40 - tenure)
        + 0.025 * (monthly_charges - 60)
        - 1.5 * contract
        + 0.4 * (internet_service == 1).astype(float)
        + 0.3 * (payment_method == 0).astype(float)
    )
    prob = 1 / (1 + np.exp(-logit))
    churn = (rng.uniform(0, 1, n_rows) < prob).astype(int)

    df = pd.DataFrame({
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "contract": contract,
        "internet_service": internet_service,
        "payment_method": payment_method,
        "churn": churn,
    })
    return df[FEATURE_NAMES + ["churn"]]


if __name__ == "__main__":
    df = generate_dataset()
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Churn rate: {df['churn'].mean():.3f}")
