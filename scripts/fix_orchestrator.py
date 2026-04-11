"""orchestrator.py에서 누락된 strategy 파일의 import/registry 엔트리 제거."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
orch = ROOT / "src" / "orchestrator.py"

# 누락된 모듈
missing = {
    "atr_expansion", "detrended_price_osc", "heikin_ashi_trend",
    "inside_bar_breakout", "klinger_oscillator", "linear_reg_channel",
    "mean_rev_band", "momentum_score", "pivot_bounce",
    "price_oscillator", "schaff_trend_cycle", "trend_continuation",
    "volume_weighted_rsi_v2", "vortex_indicator",
}

# 각 모듈에서 import하는 클래스명 찾기
content = orch.read_text()
class_names_to_remove = set()
for mod in missing:
    for m in re.finditer(rf"from src\.strategy\.{mod} import\s+(.+)", content):
        imports = m.group(1)
        for cls in re.findall(r"\w+", imports):
            class_names_to_remove.add(cls)

print(f"제거할 클래스: {sorted(class_names_to_remove)}")

lines = content.split("\n")
new_lines = []
removed_imports = 0
removed_registry = 0

for line in lines:
    skip = False
    # import 라인 제거
    m = re.match(r"from src\.strategy\.([a-z_0-9]+) import", line)
    if m and m.group(1) in missing:
        skip = True
        removed_imports += 1

    # REGISTRY 엔트리 제거: 해당 클래스를 값으로 사용하는 줄
    if not skip:
        rm = re.match(r'^\s*"([a-z_0-9]+)"\s*:\s*(\w+)', line)
        if rm and rm.group(2) in class_names_to_remove:
            skip = True
            removed_registry += 1

    if not skip:
        new_lines.append(line)

orch.write_text("\n".join(new_lines))
print(f"제거: import {removed_imports}개, REGISTRY {removed_registry}개")
