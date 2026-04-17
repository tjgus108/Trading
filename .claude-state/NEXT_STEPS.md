# Next Steps

_Last updated: 2026-04-17 (Cycle 137 완료 — SIM + 인프라 개선)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 138
- 138 mod 5 = 3 → **C(데이터) + E(실행) + SIM + F(리서치)**

### 최우선 과제 (Cycle 137 완료 후 도출)

1. **Paper Simulation 완전 실행**: 
   - Python 3.7 타입힌트 버그 수정 완료 (Cycle 137)
   - 다음: `python3 scripts/paper_simulation.py` 전체 완료 후 PASS 전략들의 walk-forward 성과 분석
   - 현재 22개 PASS 전략 중 실제 거래소 데이터(Bybit)에서의 일관성 검증 필요

2. **개선된 전략 재평가**:
   - roc_ma_cross (0.5% → 0.3%) 실제 성과 측정
   - volatility_cluster (0.5 → 0.6) 실제 성과 측정
   - QUALITY_AUDIT.csv 재실행하여 개선 효과 정량화

3. **Regime Detection 구현** (미착수 — 매우 중요):
   - `src/data/regime_detector.py` 추가 (HMM k=2~3 또는 GMM)
   - DataFeed에 regime 컬럼 주입
   - 설계안: Cycle 134 리서치 완료

4. **테스트 실패 수정** (33개):
   - 다음 A(품질) 사이클에서 처리
   - 현재: 6598 PASS, 33 FAIL

### Cycle 137 성과

**[SIM] Paper Simulation & Auto-improve:**
- 인프라: Python 3.7 타입힌트 호환성 수정 (List/Dict/Optional 사용)
- 전략 개선: roc_ma_cross, volatility_cluster 파라미터 튜닝
- 분석: 22개 PASS 전략 품질 메트릭 수집 (avg Sharpe 4.79, avg PF 1.95)

### 후속 과제 (미착수)
- Regime Detection 구현 (설계안 준비됨)
- engulfing_zone/relative_volume 심화 개선 (실거래 +5.42%, +4.95%)
- TWAP 비대칭 슬리피지 실전 데이터 검증
- paper_connector balance 실전 paper trading 검증
- Python 3.7→3.11+ 환경 격리 (선택사항)
