# Next Steps

_Last updated: 2026-06-04 (Cycle 271 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 271

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 269 | D+E+F | cmf period [20,21,22]→[21,22,23], per-strategy validator 패턴, cmf min_wfe=0.4, wick_reversal min_oos_trades=5 |
| 270 | A+C+F | cmf sharpe_decay_max=0.40 → **cmf 5/5 PASS!**, wick_reversal RSI<70 필터 (효과 미미) |
| 271 | B+D+F | EMA 필터 실험→역효과→롤백, avg_wfe 윈소라이즈, cmf_1h 파라미터 그리드 추가 |

### 🎯 Cycle 272 작업 방향 (272 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): wick_reversal ADX 필터 탐색
- EMA 방향 필터 실패 원인 분석:
  - fold1 (Aug-Oct 2023 bull run): EMA20>EMA50 → EMA filter passes → 5 trades ALL FAIL (Sharpe=-9.992)
  - 문제: EMA filter가 고위험 구간을 차단 못함 (bull run에서 Hammer = reversal, 하지만 trend 지속)
  - 핵심: wick_reversal은 range/sideways 마켓에서만 유효
- 새 방향: ADX (Average Directional Index) 필터
  - Hammer/Shooting Star: `adx14 < 25` (트렌드 약할 때만 진입)
  - ADX > 25 = 강한 트렌드 → wick 패턴 신뢰 불가
  - enrich_indicators()에 adx14 컬럼 추가 필요 (현재 없음)
  - `adx14 = 0.5*(abs(high-high_prev) - abs(low-low_prev)) / true_range`의 지수평활

#### D(ML): cmf 1h 성능 개선 전략
- cmf 1h 근본 원인 확정: period=20 = 20시간 (4h에서는 80시간)
- 1h 개선 접근: 
  - `src/backtest/walk_forward.py` DEFAULT_GRIDS cmf_1h=[60,75,90] 추가 (완료)
  - 다음 단계: paper_simulation.py에 PAPER_SIM_STRATEGY_PARAMS 딕셔너리 추가
    - cmf: period=60 (1h 최적 추정값)로 paper sim 테스트
  - 방법: `evaluate_strategy_walk_forward()` 함수에 `strategy_params: dict = None` 인자 추가
    - `strategy_inst = strategy_cls(**(strategy_params or {}))`

#### F(리서치): wick_reversal 안정화를 위한 ADX 필터 선행 연구
- ADX 임계값 25는 Wilder 기준 (강한 트렌드 = ADX > 25)
- wick_reversal 4h fold1 (Aug-Oct 2023): ADX는 강한 상승 트렌드 → ADX > 25 예상
- fold2 (Oct-Dec 2023): 급등 구간 → ADX > 25 예상 → Shooting Star 차단 가능
- 검증 방법: fold 기간별 ADX 평균 계산 후 25 기준 필터 효과 추정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 271)
- 테스트: **8369 passed, 23 skipped** (413s) — 회귀 없음
- walk_forward 테스트: **70 passed** — avg_wfe 클리핑 변경 후 이상 없음
- Paper Sim BTC: 0/22 PASS (Cycle 270과 동일, EMA filter reverted)
  - top: supertrend_multi +5.87%, cmf rank=13 AvgPF=0.90 FAIL
- Bundle OOS BTC 4h (CSV 5-fold): **1/5 PASS** (cmf PASS — Cycle 270과 동일)
  - cmf: 5/5 PASS, avg=2.508, std=1.888 ✓
  - wick_reversal: avg=-0.416 (EMA filter 적용 후 악화), reverted → avg=1.200 복원
  - wick_reversal avg_wfe 클리핑 후: -2.661 → -0.543 (더 직관적)

### 주요 코드 변경 이력 (Cycle 271)
1. `src/strategy/wick_reversal.py` — EMA 방향 필터 추가 후 롤백 (역효과 확인)
2. `src/backtest/walk_forward.py` — avg_wfe 윈소라이즈 추가 (WFE ±3.0 클리핑, 집계만)
3. `src/backtest/walk_forward.py` — DEFAULT_GRIDS에 cmf_1h 파라미터 그리드 추가

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
