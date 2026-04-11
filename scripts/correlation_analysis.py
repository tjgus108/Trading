"""
전략 간 상관관계 분석.
PASS 전략들이 실제로 서로 다른 신호를 내는지 검증.
동일 데이터에서 각 전략의 신호 시계열을 생성하고 Pearson 상관관계 계산.
"""
import importlib
import inspect
import logging
import sys
import warnings
from pathlib import Path

logging.getLogger().setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.strategy.base import BaseStrategy, Action

# quality_audit와 동일한 합성 데이터 생성기 재사용
from scripts.quality_audit import make_synthetic_data, find_strategy_classes


# QUALITY_AUDIT.csv에서 PASS 전략만 가져오기
ROOT = Path(__file__).resolve().parent.parent
csv_path = ROOT / ".claude-state" / "QUALITY_AUDIT.csv"
df_audit = pd.read_csv(csv_path)
pass_modules = set(df_audit[df_audit["passed"]]["module"].tolist())
# 삭제된 전략 제외 (재실행 가능성 대비)
strategy_dir = ROOT / "src" / "strategy"
existing = {f.stem for f in strategy_dir.glob("*.py")}
pass_modules = pass_modules & existing
print(f"PASS 전략 (현존): {len(pass_modules)}개")
print(sorted(pass_modules))
print()

# 모든 전략 클래스 중 PASS에 해당하는 것만
all_strategies = find_strategy_classes()
target_strategies = [
    (mod, cls_name, cls) for mod, cls_name, cls in all_strategies if mod in pass_modules
]
print(f"분석 대상: {len(target_strategies)}개")

# 합성 데이터에서 각 전략의 rolling 신호 생성
df = make_synthetic_data(500)

def generate_signal_series(strategy: BaseStrategy, df: pd.DataFrame) -> np.ndarray:
    """각 봉마다 strategy.generate()를 호출해 Action을 +1/-1/0으로 변환."""
    signals = []
    warmup = 52
    for i in range(warmup, len(df)):
        window = df.iloc[: i + 1].copy()
        try:
            sig = strategy.generate(window)
            val = 1 if sig.action == Action.BUY else (-1 if sig.action == Action.SELL else 0)
        except Exception:
            val = 0
        signals.append(val)
    return np.array(signals)

print("\n전략별 신호 시계열 생성 중...")
series_map: dict[str, np.ndarray] = {}
for i, (mod, cls_name, cls) in enumerate(target_strategies, 1):
    try:
        strategy = cls()
        series = generate_signal_series(strategy, df)
        series_map[strategy.name] = series
        nonzero = np.count_nonzero(series)
        print(f"  [{i:>2}/{len(target_strategies)}] {strategy.name:<30} nonzero={nonzero}")
    except Exception as e:
        print(f"  [ERR] {mod}: {str(e)[:60]}")

if not series_map:
    print("분석 가능한 전략 없음")
    sys.exit(1)

# 상관관계 행렬
names = sorted(series_map.keys())
data = np.stack([series_map[n] for n in names])
# 각 시리즈 정규화 (분산이 0이면 NaN 방지)
corr_matrix = np.zeros((len(names), len(names)))
for i in range(len(names)):
    for j in range(len(names)):
        a, b = data[i], data[j]
        if np.std(a) == 0 or np.std(b) == 0:
            corr_matrix[i, j] = 0.0 if i != j else 1.0
        else:
            corr_matrix[i, j] = np.corrcoef(a, b)[0, 1]

corr_df = pd.DataFrame(corr_matrix, index=names, columns=names)

# 높은 상관관계 쌍 식별
print("\n=== 높은 상관관계 쌍 (|corr| >= 0.7) ===")
high_corr_pairs = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        c = corr_matrix[i, j]
        if abs(c) >= 0.7:
            high_corr_pairs.append((names[i], names[j], c))

high_corr_pairs.sort(key=lambda x: -abs(x[2]))
for a, b, c in high_corr_pairs:
    print(f"  {c:>+.3f}  {a:<25} <-> {b}")

print(f"\n총 쌍: {len(high_corr_pairs)}개")

# 다양성 있는 전략 선택 (상관관계 < 0.7인 전략들)
print("\n=== 다양성 있는 전략 선정 (greedy) ===")
selected = []
for name in names:
    conflict = False
    for sel in selected:
        i, j = names.index(name), names.index(sel)
        if abs(corr_matrix[i, j]) >= 0.7:
            conflict = True
            break
    if not conflict:
        selected.append(name)

print(f"최종 다양성 전략: {len(selected)}개")
for s in selected:
    print(f"  - {s}")

# CSV 저장
corr_df.to_csv(ROOT / ".claude-state" / "CORRELATION_MATRIX.csv")

# 마크다운 리포트 작성
report_path = ROOT / ".claude-state" / "CORRELATION_REPORT.md"
with open(report_path, "w") as f:
    f.write("# 전략 상관관계 분석 리포트\n\n")
    f.write("_Generated: 2026-04-11_\n")
    f.write(f"_데이터: 합성 OHLCV 500 캔들 (quality_audit와 동일)_\n\n")
    f.write(f"## 분석 범위\n\n")
    f.write(f"QUALITY_AUDIT.csv의 PASS 전략 중 현재 코드베이스에 존재하는 {len(target_strategies)}개.\n\n")
    f.write("## 결과\n\n")
    f.write(f"| 항목 | 수치 |\n")
    f.write(f"|------|------|\n")
    f.write(f"| 분석 전략 | {len(series_map)}개 |\n")
    f.write(f"| 높은 상관 쌍 (\\|r\\| ≥ 0.7) | {len(high_corr_pairs)}개 |\n")
    f.write(f"| 다양성 선정 (greedy) | {len(selected)}개 |\n\n")

    f.write("## 🔥 높은 상관관계 쌍\n\n")
    f.write("상관계수 절대값 0.7 이상 — 하나는 중복으로 판단.\n\n")
    if high_corr_pairs:
        f.write("| Corr | Strategy A | Strategy B |\n")
        f.write("|------|-----------|------------|\n")
        for a, b, c in high_corr_pairs:
            f.write(f"| {c:+.3f} | `{a}` | `{b}` |\n")
    else:
        f.write("_(없음)_\n")
    f.write("\n")

    f.write("## ✅ 다양성 확보된 전략 (Greedy 선정)\n\n")
    f.write("상관관계 0.7 미만의 전략들만 남긴 포트폴리오. 이 조합으로 앙상블 시 분산 효과 최대.\n\n")
    for s in selected:
        f.write(f"- `{s}`\n")
    f.write("\n")

    f.write("## 📁 결과 파일\n\n")
    f.write("- `.claude-state/CORRELATION_MATRIX.csv` — 전체 상관 행렬\n")
    f.write("- `scripts/correlation_analysis.py` — 재실행용 스크립트\n")

print(f"\n저장:")
print(f"  {report_path}")
print(f"  {ROOT / '.claude-state' / 'CORRELATION_MATRIX.csv'}")
