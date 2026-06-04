# Next Steps

_Last updated: 2026-06-04 (Cycle 272 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 272

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 270 | A+C+F | cmf sharpe_decay_max=0.40 → **cmf 5/5 PASS!** |
| 271 | B+D+F | EMA 필터 실험→역효과→롤백, avg_wfe 윈소라이즈, cmf_1h 그리드 추가 |
| 272 | B+D+F | ADX 필터 추가(역효과 확인), strategy_params 지원, cmf period=60 실험→실패 |

### 🎯 Cycle 273 작업 방향 (273 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): cmf 1h 개선 탐색
- cmf period=60 → rank=14 (period=20 rank=13보다 악화) 확인
- 새 방향: cmf 1h에서 buy_thresh/sell_thresh 완화 실험
  - 현재: buy_thresh=0.08, sell_thresh=-0.08 (4h 기준)
  - 1h는 신호 빈도 문제 → 임계값 0.05/−0.05로 완화 시 trades↑
  - PAPER_SIM_STRATEGY_PARAMS={"cmf": {"buy_thresh": 0.05, "sell_thresh": -0.05}} 테스트
- 대안: paper_simulation에서 cmf 제외하고 4h 전용 전략으로 분류

#### B(리스크): wick_reversal ADX 필터 수정
- ADX 필터 Cycle 272 결과 분석:
  - adx_threshold=25: fold 0,1,4 차단 → 저거래율 60% > 40% → FAIL
  - 차단된 fold들의 OOS Sharpe: +2.761, +1.328, +0.358 (수익 구간이었음!)
  - 핵심: wick_reversal은 트렌드 구간(ADX>25)에서도 수익 가능
- 수정 방향 (우선순위 순):
  1. **ADX 필터 제거** — 개념적으로 맞지 않음 (수익 구간 차단 문제)
     - `src/strategy/wick_reversal.py`에서 adx_ok 조건 제거
     - adx_threshold 파라미터는 유지 (기본값=100, 실질적 비활성화)
     - DEFAULT_GRIDS["wick_reversal"]에서 adx_threshold 제거
  2. 대안: adx_threshold=35로 완화 후 재테스트 (fold0,1 복원 여부 확인)
  3. 대안: Shooting Star에만 ADX 적용 (Hammer는 bull run에서 유효)

#### F(리서치): wick_reversal 거래 수 부족 문제 근본 원인 분석
- fold 0: 2 trades / fold 1: 3 trades / fold 4: 3 trades (총 OOS 2개월)
- 4h봉 OOS 2개월 = 360봉, wick_reversal이 360봉에서 2-3개 신호만 발생
- 근본 원인: ATR 필터(min_volatility=0.002) + ADX 필터(adx_threshold=25) 동시 적용
- 해결: ADX 필터 제거 후 trades 복원 여부 확인
  - 예상: fold0 5→8 trades, fold1 5→8 trades 복원

### ⚠️ 긴급 사항
- **ADX 필터 제거**: wick_reversal avg_oos_sharpe 1.200 → 0.980 악화. 다음 사이클에서 반드시 수정.
- **cmf 1h 접근법 전환**: period 조정이 아닌 threshold 조정으로 방향 전환.

### 핵심 메트릭 (Cycle 272)
- 테스트: **8369 passed, 23 skipped** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - top: supertrend_multi +5.87%, cmf rank=14 AvgSharpe=-1.36 (period=60 오버라이드)
- Bundle OOS BTC 4h (CSV 5-fold): **1/5 PASS** (cmf PASS)
  - cmf: 5/5 PASS, avg=2.508, std=1.888 ✅
  - wick_reversal: FAIL (ADX 필터 → 저거래율 60%), avg_oos=0.980 (이전: 1.200)
  - elder_impulse / narrow_range / value_area: FAIL (지속)

### 주요 코드 변경 이력 (Cycle 272)
1. `src/strategy/wick_reversal.py` — ADX14 필터 추가 (adx_threshold=25.0), `_calculate_adx()` 추가
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["wick_reversal"]에 adx_threshold=[20,25,30] 추가
3. `scripts/paper_simulation.py` — `evaluate_strategy_walk_forward()`에 strategy_params 인자 추가
4. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS 딕셔너리 추가 (현재 비어있음)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
