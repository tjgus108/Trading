"""품질 감사 결과 분석 → 삭제 대상 선별."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv_path = ROOT / ".claude-state" / "QUALITY_AUDIT.csv"
df = pd.read_csv(csv_path)

print(f"총 전략: {len(df)}")
print(f"컬럼: {list(df.columns)}")
print()

# 1. 거래 횟수 부족 (< 5회) — 명백한 실패
low_trades = df[df["trades"] < 5].copy()
print(f"=== 거래 <5회 전략 ({len(low_trades)}개) ===")
for _, r in low_trades.sort_values("trades").iterrows():
    print(f"  {r['module']:<40} trades={int(r['trades']):>3} sharpe={r['sharpe']:>6.2f}")
print()

# 2. 거래 0회 (신호 전혀 안 나옴) — 절대 실패
no_trades = df[df["trades"] == 0].copy()
print(f"=== 거래 0회 전략 ({len(no_trades)}개) ===")
for _, r in no_trades.iterrows():
    print(f"  {r['module']:<40}")
print()

# 3. 중복 전략 탐지: (sharpe, win_rate, profit_factor, trades) 튜플 완전 일치
grouped = df.groupby(["sharpe", "win_rate", "profit_factor", "trades", "max_dd"])
dup_groups = [g for _, g in grouped if len(g) > 1]
# 거래 0인 중복은 제외 (모두 똑같이 0 나오니까)
dup_groups = [g for g in dup_groups if g["trades"].iloc[0] > 0]

print(f"=== 중복 전략 그룹 ({len(dup_groups)}개) ===")
duplicates_to_remove = []
for g in dup_groups:
    modules = list(g["module"])
    s = g.iloc[0]
    print(f"  [S={s['sharpe']:.2f} WR={s['win_rate']:.2%} PF={s['profit_factor']:.2f} T={int(s['trades'])}]")
    for i, m in enumerate(modules):
        marker = "KEEP" if i == 0 else "REMOVE"
        print(f"    {marker}: {m}")
        if i > 0:
            duplicates_to_remove.append(m)
print()
print(f"중복 제거 대상: {len(duplicates_to_remove)}개")
print()

# 4. 명백한 FAIL: trades < 5 or trades == 0
delete_set = set(low_trades["module"].tolist())
delete_set.update(duplicates_to_remove)

print(f"=== 총 삭제 대상 ({len(delete_set)}개) ===")
for m in sorted(delete_set):
    print(f"  {m}")

# 파일로 저장
out_path = ROOT / ".claude-state" / "DELETE_TARGETS.txt"
with open(out_path, "w") as f:
    for m in sorted(delete_set):
        f.write(m + "\n")
print(f"\n저장: {out_path}")
