import json
from pathlib import Path

FEATURE_STORE_PATH = Path("feature_store/features.json")

FEATURE_NAMES = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "contract",
    "internet_service",
    "payment_method",
]

FEATURE_SCHEMA = {
    "tenure": {"type": "int", "min": 0, "max": 72, "desc": "Месяцев в подписке"},
    "monthly_charges": {"type": "float", "min": 18.0, "max": 120.0, "desc": "Ежемесячная плата, USD"},
    "total_charges": {"type": "float", "min": 0.0, "max": 9000.0, "desc": "Суммарные платежи, USD"},
    "contract": {"type": "int", "values": [0, 1, 2], "desc": "0 = month, 1 = year, 2 = two years"},
    "internet_service": {"type": "int", "values": [0, 1, 2], "desc": "0 = DSL, 1 = fiber, 2 = none"},
    "payment_method": {"type": "int", "values": [0, 1, 2, 3], "desc": "Способ оплаты"},
}


def init_feature_store():
    FEATURE_STORE_PATH.parent.mkdir(exist_ok=True, parents=True)
    with FEATURE_STORE_PATH.open("w", encoding="utf-8") as f:
        json.dump(FEATURE_SCHEMA, f, indent=2, ensure_ascii=False)


def load_schema():
    if not FEATURE_STORE_PATH.exists():
        init_feature_store()
    with FEATURE_STORE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    init_feature_store()
    print(f"Feature store initialized at {FEATURE_STORE_PATH}")
