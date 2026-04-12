"""
품질 감사 결과 기반 전략 자동 삭제 스크립트.
DELETE_TARGETS.txt 리스트에 있는 전략의:
1. src/strategy/*.py 파일 삭제
2. src/orchestrator.py의 import 라인 제거
3. STRATEGY_REGISTRY 엔트리 제거
4. tests/test_*.py 관련 테스트 파일 삭제
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
targets_path = ROOT / ".claude-state" / "DELETE_TARGETS.txt"

# 보존할 핵심 전략 (합성 데이터에서 0 거래지만 실전에서 유효할 수 있음)
# - 표준 캔들 패턴 (실전에서 가끔 발생)
# - 외부 데이터 필요한 ML/LOB/GEX 전략
KEEP = {
    # 캔들 패턴 (실전에서 유효)
    "doji_pattern", "harami", "marubozu", "three_candles",
    "morning_evening_star", "three_soldiers_crows", "star_pattern",
    "engulfing",  # 단, 중복이라 삭제됨 - KEEP에서 제외
    "candle_pattern", "candle_pattern_score", "candle_body_filter",
    # ML/외부 데이터 의존
    "ml_strategy", "lstm_strategy", "heston_lstm_strategy",
    "market_maker_sig", "gex_strategy", "smc_strategy",
    # 핵심 전략 (실전에서 유효)
    "supertrend", "vortex",
}

# 하지만 중복은 무조건 삭제 (engulfing, nr7, zero_lag_ema, trend_channel, elder_ray)
FORCE_DELETE = {"engulfing", "nr7", "zero_lag_ema", "trend_channel", "elder_ray"}

targets = [l.strip() for l in targets_path.read_text().splitlines() if l.strip()]
print(f"원본 삭제 대상: {len(targets)}개")

# 실제 삭제 대상: (targets - KEEP) + FORCE_DELETE
final_delete = set()
for t in targets:
    if t in FORCE_DELETE:
        final_delete.add(t)
    elif t not in KEEP:
        final_delete.add(t)

print(f"최종 삭제: {len(final_delete)}개")
print(f"보존(실전 유효 가능): {sorted(set(targets) - final_delete)}")
print()

# 1. 전략 파일 삭제
strategy_dir = ROOT / "src" / "strategy"
tests_dir = ROOT / "tests"
deleted_files = []

for name in sorted(final_delete):
    sf = strategy_dir / f"{name}.py"
    if sf.exists():
        sf.unlink()
        deleted_files.append(str(sf.relative_to(ROOT)))
    # 대응 테스트 파일도 삭제
    tf = tests_dir / f"test_{name}.py"
    if tf.exists():
        tf.unlink()
        deleted_files.append(str(tf.relative_to(ROOT)))

print(f"삭제된 파일: {len(deleted_files)}개")

# 2. orchestrator.py import 라인 + REGISTRY 엔트리 제거
orch_path = ROOT / "src" / "orchestrator.py"
content = orch_path.read_text()
original_lines = content.split("\n")
new_lines = []

removed_imports = 0
removed_registry = 0

for line in original_lines:
    skip = False
    # import 라인 확인: "from src.strategy.<name> import ..."
    m = re.match(r"from src\.strategy\.([a-z_0-9]+) import", line)
    if m and m.group(1) in final_delete:
        skip = True
        removed_imports += 1

    # STRATEGY_REGISTRY 엔트리: '    "<name>": SomeStrategy,'
    # 해당 전략명이 딱 하나 쓰인 경우 (e.g., "nr7": NR7Strategy,)
    if not skip:
        rm = re.match(r'^\s*"([a-z_0-9]+)"\s*:\s*\w+,?\s*$', line)
        if rm and rm.group(1) in final_delete:
            skip = True
            removed_registry += 1

    if not skip:
        new_lines.append(line)

new_content = "\n".join(new_lines)
orch_path.write_text(new_content)
print(f"orchestrator.py: import {removed_imports}개, REGISTRY {removed_registry}개 제거")

# 결과 저장
summary_path = ROOT / ".claude-state" / "CLEANUP_SUMMARY.txt"
with open(summary_path, "w") as f:
    f.write(f"Cleanup Summary\n")
    f.write(f"===============\n\n")
    f.write(f"Deleted strategies: {len(final_delete)}\n")
    f.write(f"Deleted files: {len(deleted_files)}\n")
    f.write(f"Removed imports: {removed_imports}\n")
    f.write(f"Removed REGISTRY entries: {removed_registry}\n\n")
    f.write(f"Deleted strategy list:\n")
    for name in sorted(final_delete):
        f.write(f"  {name}\n")
print(f"\n저장: {summary_path}")
