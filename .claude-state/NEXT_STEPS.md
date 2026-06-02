# Next Steps

_Last updated: 2026-06-02 (Cycle 263 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 263

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 262 | B+D+F | RiskManager ATR 자동연계, momentum_persistence 피처 (20피처) |
| 263 | C+B+F | cmf 파라미터 범위 축소 (buy_thresh/period), DrawdownMonitor 컴포넌트별 로그 |

### 🎯 Cycle 264 작업 방향 (264 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): momentum_persistence 피처 효과 분석
- Cycle 263 시뮬에서 SOL/ETH 모두 Score 미변동 — 피처가 RF모델에서 실제 사용되는지 확인 필요
- 방향: `src/ml/features.py`의 RandomForest feature_importances_ 로그 추가 또는 테스트 작성
  - 피처 중요도 최하위 5개 확인 후 필요시 제거 or 대체 피처 탐색
- 또는: momentum_persistence 대신 `trend_age` (추세 시작 이후 봉 수) 피처로 교체 검토

#### E(실행): wick_reversal 0거래 문제 해결
- Bundle OOS와 Paper Sim 모두 wick_reversal은 거래 0건
- min_oos_trades=10 필터에 의해 집계 제외됨 → 신호 자체가 없음
- 방향: `src/strategy/wick_reversal.py` 신호 조건 완화
  - vol_percentile (현재 0.85) → 0.70~0.75로 낮추어 신호 빈도 증가
  - min_wick_ratio (현재 0.60-0.70) → 0.50-0.65로 하향 조정 검토
- 주의: 조건 완화 후 반드시 테스트 통과 확인

#### F(리서치): cmf WFE 역전 현상 대응 방안 연구
- cmf fold 0: IS=-1.499, OOS=5.111 → WFE=0 강제 (IS<-1.0 규칙)
- 분석: 레짐 의존적 구조이므로 WFE=0이 적절하지 않음
- 방향: `src/backtest/walk_forward.py` RollingOOSValidator.validate()에서
  - IS < -1.0 AND OOS > 2.0인 경우 → WFE=0.5 (regime change marker) 적용 검토
  - 단, 이 변경은 기준 완화이므로 신중히 처리

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 가능 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: synthetic CSV 사용 (data/historical/synthetic/ETHUSDT|SOLUSDT/1h.csv)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 263)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi 72.6점, Sharpe=0.43, PF=1.13)
- Paper Sim ETH: 0/22 (top: momentum_quality 65.8점, Sharpe=0.73, PF=1.17)
- Paper Sim SOL: 0/22 (top: momentum_quality 75.0점, Sharpe=0.26, PF=1.12)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (cmf 93.6점, avg OOS Sharpe=2.508, std=1.888)

### 주요 코드 변경 이력 (Cycle 263)
1. `src/backtest/walk_forward.py` — cmf DEFAULT_GRIDS 파라미터 범위 축소
   - period: [15,20,25]→[18,20,22], buy_thresh: [0.06,0.08,0.10]→[0.07,0.08,0.09]
2. `src/risk/manager.py` — DrawdownMonitor size_mult 로그에 streak/MDD/ATR 컴포넌트 분리 추가
