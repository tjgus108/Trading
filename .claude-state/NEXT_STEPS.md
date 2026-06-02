# Next Steps

_Last updated: 2026-06-02 (Cycle 262 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 262

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 261 | B+D+F | DrawdownMonitor ATR필터, FeatureBuilder atr_vol_regime (19피처) |
| 262 | B+D+F | RiskManager ATR 자동연계, momentum_persistence 피처 (20피처) |

### 🎯 Cycle 263 작업 방향 (263 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): cmf 전략 안정성 개선 (OOS Sharpe std 감소)
- Bundle OOS에서 cmf가 2/5 PASS이지만 std=1.888 > 1.5 (불안정)
- 방향: `src/backtest/walk_forward.py`의 Bundle 구성 파라미터 검토
  - 각 fold의 IS/OOS 기간 비율 조정 (현재 4h × 5 fold)
  - min_oos_trades 기준이 너무 낮은지 확인 (현재 10 trades)
- 또는: cmf 전략의 파라미터 범위 축소하여 안정화

#### B(리스크): HIGH_VOL 레짐에서 포지션 과도 감소 검토
- Cycle 262 RiskManager에 ATR 자동연계 추가
- 다음: paper_simulation의 실제 포지션 사이즈가 ATR 필터로 얼마나 감소하는지 로그 분석
  - 특히 강세장 구간(w4-w7)에서 신호가 걸리는지 확인
  - src/risk/manager.py 로그에서 "DrawdownMonitor size_mult" 라인 확인

#### F(리서치): momentum_persistence 효과 검증
- Cycle 262 추가한 momentum_persistence: SOL 75.0점 (ETH 65.8점) — SOL에 더 효과적
- 다음 시뮬에서 momentum_quality SOL PF 1.12 → 1.5 이상으로 개선 여부 모니터링
- cmf fold 0의 IS=-1.499 → OOS=5.111 역전 현상 분석: 과적합이 아닌 비모수 구조 의심

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 가능 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: GARCH OU CSV 사용 (ETH: 680-5955, SOL: 12-247)
- Bundle OOS: `--csv-dir data/historical` 필수 (미지정 시 합성 데이터로 9 fold)

### 핵심 메트릭 (Cycle 262)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi 72.6점, Sharpe=0.43, PF=1.13)
- Paper Sim ETH: 0/22 (top: momentum_quality 65.8점, Sharpe=0.73, PF=1.17)
- Paper Sim SOL: 0/22 (top: momentum_quality 75.0점, Sharpe=0.26, PF=1.12) ← SOL 첫 기록
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (cmf 93.6점, avg OOS Sharpe=2.508, std=1.888)

### 주요 코드 변경 이력 (Cycle 262)
1. `src/risk/manager.py` — evaluate()에 DrawdownMonitor.set_atr_state() 자동 호출 추가
2. `src/ml/features.py` — momentum_persistence 피처 추가, feature_names 19→20개
3. `tests/test_feature_builder.py` — test_returns_19 → test_returns_20
4. `tests/test_fr_oi_pipeline_e2e.py` — 피처 카운트 업데이트 (Cycle 261 누락분 포함)
5. `tests/test_funding_oi_feed.py` — 피처 카운트 업데이트
