# Current Cycle Briefing

_Cycle 345 | 2026-06-22 | A(품질) + C(데이터) + F(리서치)_

## 완료된 사이클: 345
**카테고리**: A(품질) + C(데이터) + F(리서치)

### A(품질): BundleOOSResult avg_oos_mdd 테스트 추가

**작업**:
- `tests/test_walk_forward.py`에 5개 테스트 추가:
  - None → summary에 avg_oos_mdd 줄 없음
  - 0.05 → "5.00% (LOW)"
  - 0.10 → "MED" (> 0.08 이상)
  - 0.16 → "HIGH" (> 0.15 이상)
  - 0.08 경계값 → "LOW" (정확히 0.08 = NOT > 0.08 = LOW)
- RANGING 관련 테스트 전체 점검: 232개 통과, 추가 불일치 없음

### C(데이터): cumulative VWAP → rolling(20) VWAP 교체

**분석 결과**:
- `df["vwap"]` 직접 사용: `vwap_reversion.py` (sharpe=-6.55, FAIL), `ema_cross.py` (fallback)
- Bundle OOS 5개 전략은 내부 VWAP 직접 계산 → 영향 없음
- cumulative VWAP: 12000봉 기준 현재 close와 최대 6.1% 편차 (rolling(20) = 1.3%)

**코드 개선**:
- `scripts/paper_simulation.py` + `scripts/run_bundle_oos.py` 수정
- `enrich_indicators()`에서 cumulative → rolling(20) 교체
- `df["vwap20"]` 도 rolling(20)으로 통일 (vwap == vwap20)

### F(리서치): min_hold_bars=4 실험 — 신호 노이즈 감소 검증

**실험 결과** (`--min-hold-bars 4`, BTC only, 1h, 8-fold):

| 전략 | Baseline | MHB4 | 변화 |
|------|----------|------|------|
| roc_ma_cross | 0.34 | **0.99** | +0.65 ↑ |
| price_action_momentum | -1.08 | +0.37 | +1.45 ↑ |
| lob_maker | -0.04 | +0.63 | +0.67 ↑ |
| price_cluster | **0.87** | 0.27 | -0.60 ↓ |
| cmf | -1.23 | -1.31 | -0.08 ↓ |

**결론**:
- min_hold_bars=4는 roc_ma_cross 0.34→0.99로 대폭 개선 (PF=1.34로 거의 PASS)
- cmf 신호 노이즈 미해결 (trades 68→56, not 17)
- price_cluster 악화 (희소 신호가 차단됨)
- **전역 설정보다 전략별 min_hold_bars 필요** → Cycle 346 D(ML) 과제

## 시뮬레이션 결과

### Paper Simulation (1h, 8-fold, BTC/ETH/SOL)
- **PASS: 0/20** (BTC: 25연속)
- BTC Top: price_cluster (Sharpe=0.87, 1/8), roc_ma_cross (Sharpe=0.34, 2/8)
- ETH Top: price_action_momentum (0.23), volatility_cluster (0.82) — synthetic
- SOL Top: momentum_quality (-0.17), order_flow_imbalance_v2 (-0.37) — synthetic
- VWAP 수정 후 BTC 결과 완전 동일 (vwap_reversion/ema_cross 미포함)

### Bundle OOS (4h, BTC/USDT)
- **PASS: 5/5** ✅ (유지)
- avg_oos_mdd: cmf=5.19%, OFI v2=3.36%, supertrend=2.23%, vwap=2.67%, value_area=1.87%
- #1 order_flow_imbalance_v2 (Score=62.0, OOS Sharpe=4.345)
- VWAP 수정 영향 없음 (내부 계산 사용)

## 테스트 결과

- **8432 passed, 0 failed** (Cycle 344의 8427 + 5개 avg_oos_mdd 테스트 추가)

## 다음 사이클 (346) 방향

346 mod 5 = 1 → **B(리스크) + D(ML)**

1. **D(ML)**: per-strategy min_hold_bars 지원 추가
   - `PAPER_SIM_MIN_HOLD_BARS: Dict[str, int]` 딕셔너리 추가
   - engine을 전략별로 별도 생성 (min_hold_bars 오버라이드)
   - `roc_ma_cross: 4` 설정 → Sharpe 0.34→0.99 기대

2. **B(리스크)**: roc_ma_cross PF 개선 분석
   - min_hold_bars=4 시 PF=1.34 (필요 PF=1.5)
   - 실패 원인: "profit_factor 1.15 < 1.5 (x1)" — 1개 창에서 PF 미달
   - TP 비율 또는 entry filter 조정 탐색
