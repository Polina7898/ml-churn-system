from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

OUTPUT_DIR = Path("docs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
N = 500_000

rng = np.random.default_rng(42)
existing = rng.normal(loc=3.5, scale=0.4, size=N)
improved = rng.normal(loc=2.0, scale=0.4, size=N)


def main():
    u_stat, p_value = stats.mannwhitneyu(existing, improved, alternative="two-sided")
    t_stat, t_p = stats.ttest_ind(existing, improved, equal_var=False)
    cohen_d = (existing.mean() - improved.mean()) / np.sqrt(
        (existing.std(ddof=1) ** 2 + improved.std(ddof=1) ** 2) / 2
    )

    print("H0: распределения времени отклика обеих систем одинаковы")
    print("H1: распределения отличаются (улучшенная система быстрее)")
    print(f"alpha = {ALPHA}")
    print(f"n existing = {len(existing)}, n improved = {len(improved)}")
    print()
    print(f"Mann-Whitney U: U = {u_stat:.3e}, p = {p_value:.3e}")
    print(f"Welch t-test:   t = {t_stat:.3f},   p = {t_p:.3e}")
    print(f"Cohen's d: {cohen_d:.3f}")
    print()
    print(f"mean(v1) = {existing.mean():.3f} с,   mean(v2) = {improved.mean():.3f} с")
    print(f"median(v1) = {np.median(existing):.3f} с, median(v2) = {np.median(improved):.3f} с")
    print(f"p95(v1) = {np.percentile(existing, 95):.3f} с, p95(v2) = {np.percentile(improved, 95):.3f} с")
    print()
    if p_value < ALPHA:
        print(f"Решение: p-value < {ALPHA} → H0 отклоняем, различия статистически значимы")
        print("Действие: внедряем архитектуру v2 в продакшен")
    else:
        print("Решение: H0 не отклоняем, различия не значимы")

    plt.figure(figsize=(10, 6))
    sns.kdeplot(existing, label="Существующая система (v1)", fill=True, color="red")
    sns.kdeplot(improved, label="Улучшенная система (v2)", fill=True, color="green")
    plt.title("Сравнение распределений времени отклика")
    plt.xlabel("Время отклика, с")
    plt.ylabel("Плотность")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(OUTPUT_DIR / "latency_comparison.png", dpi=120, bbox_inches="tight")
    plt.close()
    print(f"\nГрафик сохранён: {OUTPUT_DIR / 'latency_comparison.png'}")


if __name__ == "__main__":
    main()
