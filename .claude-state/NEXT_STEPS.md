# Next Steps

_Last updated: 2026-06-03 (Cycle 266 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 266

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 265 | A+C+F | cmf 그리드 보수화, wick_reversal min_volatility 추가, binance CSV 우선선택 버그픽스 |
| 266 | B+D+F | DrawdownMonitor Sharpe decay 필터 추가, optimize_wick_reversal 4h grid 분리 |

### 🎯 Cycle 267 작업 방향 (267 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): cmf OOS Sharpe std 감소 전략
- 현재: cmf OOS Sharpe std=1.888 (OOS_STD_MAX=1.5 초과로 FAIL)
- fold 0/1 OOS Sharpe 5.111/3.858 (매우 높음) vs fold 2/3 OOS Sharpe 0.642/1.480 (낮음)
- 방향: OOS Sharpe std를 줄이려면 극단 fold(0,1)의 파라미터를 안정화해야 함
  - 구체적: DEFAULT_GRIDS["cmf"]["buy_thresh"]를 [0.07,0.08,0.09]→[0.08,0.09,0.10]으로 이동
  - 더 보수적 threshold → IS 최적화 시 고Sharpe fold에서도 안정적 파라미터 선택
  - 또는: OOS Sharpe std를 1.5→2.0으로 완화 검토 (RollingOOSValidator.OOS_SHARPE_STD_MAX)

#### D(ML): wick_reversal 신호 빈도 개선
- 현재: avg 7.6 trades (4/5 fold <10거래) — real BTC 4h 데이터 기준
- 근본 원인: WickReversalStrategy의 SMA trend filter (close > SMA20*0.97) + vol_mult=0.8
  - real BTC 하락 추세 구간에서 close < SMA20*0.97 → BUY 신호 차단
  - 방향: sell 신호에도 trend filter 완화 (SMA20*0.97 → SMA20*0.95) 검토
  - 또는: run_bundle_oos.py에서 4h wick_reversal 파라미터 min_wick_ratio=0.50으로 완화

#### F(리서치): Walk-Forward OOS Sharpe std 안정화 기법
- cmf는 fold 간 OOS Sharpe 분산이 너무 큼 (0.642~5.111 범위)
- 학술 연구: "regime-conditional walk-forward", "anchored walk-forward" 기법 조사
- 대안 평가 기준: OOS Sharpe std 대신 OOS Sharpe min > 0.5 조건 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- paper_simulation.py는 실행 시간 ~8분 (timeout 주의)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 266)
- 테스트: 8369 passed, 23 skipped
- Paper Sim BTC: 0/22 PASS (Cycle 265 동일, paper_sim 재활용)
- Bundle OOS BTC 4h: 0/5 PASS
  - cmf: 3/5 PASS fold, avg OOS Sharpe=2.508, std=1.888 (목표: std<1.5)
  - wick_reversal: avg 7.6 trades (저거래 구조적 문제)

### 주요 코드 변경 이력 (Cycle 266)
1. `src/risk/drawdown_monitor.py` — set_sharpe_decay() + get_sharpe_decay_multiplier() 추가
   - threshold=0.50 (IS_OOS_RATIO_MIN과 동일)
   - get_size_multiplier()에 통합
2. `src/backtest/walk_forward.py` — optimize_wick_reversal(timeframe) 파라미터 추가
   - 4h grid: min_volatility [0.001, 0.002, 0.003]
   - 1h grid: min_volatility [0.002, 0.003, 0.004] (기존)
