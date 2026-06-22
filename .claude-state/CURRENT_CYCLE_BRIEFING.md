# Current Cycle Briefing

_Cycle 346 | 2026-06-22 | B(리스크) + D(ML) + F(리서치)_

## 완료된 사이클: 346

### 핵심 변경사항

1. **RANGING 레짐 스톱 바운드 추가** (`src/risk/manager.py`)
   - `_REGIME_STOP_BOUNDS`에 RANGING 항목 신규 추가
   - `"RANGING": (1.5, 2.5)` — floor=1.5 (횡보 노이즈 흡수), ceiling=2.5 (과도한 스톱 방지)
   - 배경: 기존 RANGING은 bounds 없음 → 저변동 RANGING에서 vol-based 1.2배 → 노이즈에 손절 피격
   - 효과: RANGING에서 최소 1.5xATR 스톱 거리 보장 → 정상 횡보 진동에 조기 손절 방지

2. **frama signal_thresh 파라미터화** (`src/strategy/frama.py`)
   - `gap_pct >= 1.0` (하드코딩) → `gap_pct >= self.signal_thresh` (파라미터)
   - 기본값 signal_thresh=1.0 유지 (하위 호환)
   - WFO가 0.5/1.0/1.5% 탐색하여 횡보 노이즈 vs 추세 민감도 최적값 발견 가능

3. **frama WFO 그리드 확장** (`src/backtest/walk_forward.py`)
   - `signal_thresh: [0.5, 1.0, 1.5]` 추가
   - 9조합 (period×rsi_period) → 27조합 (period×rsi_period×signal_thresh)
   - signal_thresh=1.5: 강한 이격만 진입 → RANGING에서 잡음 신호 차단
   - signal_thresh=0.5: 작은 이격에도 진입 → 추세 초기 포착 가능

### D(ML) 관찰: price_cluster vol_regime_filter 효과

- Cycle 345에서 WFO 그리드에 vol_regime_filter=True 추가
- 이번 paper_sim 결과: price_cluster AvgTrades=41, Sharpe=0.87 (변화 없음)
- 해석: 8개 OOS 윈도우 모두 RANGING 도미넌트 → vol_regime_filter=True가 모든 RANGING 진입 차단보다는 특정 vol_atr_trend_min 임계값 이상만 차단
- 즉 낮은 vol_atr_trend_min(1.5) 선택 시 ATR/ATR_MA < 1.5인 구간만 진입 허용 → 거래 수 감소 안 함(대부분 구간이 ATR/ATR_MA < 1.5인 저변동 RANGING)

### 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| Paper Sim 1h BTC | 0/20 PASS (26연속) |
| Bundle OOS 4h | 5/5 PASS |
| price_cluster Sharpe | 0.87 (유지) |
| frama Sharpe | 0.24, 1/8 Consistency |
| Bundle OOS MDD | cmf5.2/OFI3.4/ST2.2/VA2.7/VA1.9% |

### 다음 사이클 (347)

- **카테고리**: C(데이터) + E(실행) + F(리서치) (347 mod 5 = 2)
- **핵심 확인**: frama signal_thresh WFO 결과 — 다음 시뮬에서 signal_thresh 최적값 (0.5 vs 1.0 vs 1.5) 비교
- **C(데이터)**: price_cluster vol_regime_filter 효과 재분석 (vol_atr_trend_min 선택값 확인)
