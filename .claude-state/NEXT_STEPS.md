# Next Steps

_Last updated: 2026-06-02 (Cycle 261 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 260~261

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 260 | A+C+F | MC 1000 perms, ETH GARCH max→5955, market_state 태그 |
| 261 | B+D+F | DrawdownMonitor ATR필터, FeatureBuilder atr_vol_regime |

### 🎯 Cycle 262 작업 방향 (262 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): ATR 필터 → RiskManager 연계 검토
- Cycle 261에서 DrawdownMonitor.set_atr_state() 추가
- 다음: RiskManager.check() 내부에서 ATR를 DrawdownMonitor에 전달하는 로직 연계
  - src/risk/manager.py의 RiskManager.check() 시그니처에 `atr_ma` 파라미터 추가 검토
  - 또는 RiskManager.update_market_context(df) 형태의 메서드 추가

#### D(ML): atr_vol_regime 피처 효과 검증
- Cycle 261에서 FeatureBuilder에 atr_vol_regime 피처 추가
- 다음 시뮬레이션에서 momentum_quality 성과 변화 모니터링 필요
- ETH: Sharpe=0.73, PF=1.17, Score=65.8 → 목표: PF≥1.5
- SOL: 시뮬레이션 누락 → scripts/paper_simulation.py SOL 포함 확인 필요

#### F(리서치): mc_p_value 실패 원인 분석
- 주요 FAIL: mc_p_value > 0.05 (우연 가능성) — 거래 수가 적거나 신호가 약함
- 방향: 더 많은 거래(Trades↑) 또는 더 높은 win-rate 신호 강화
- supertrend_multi가 2사이클 연속 BTC 1위 → 이 전략 계열의 특성 분석

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 가능 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: GARCH OU CSV 사용 (ETH: 680-5955, SOL: 12-247)
- Bundle OOS: `--csv-dir data/historical` 필수 (미지정 시 합성 데이터로 9 fold)

### 핵심 메트릭 (Cycle 261)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi 86.6점, Sharpe=0.43, PF=1.13)
- Paper Sim ETH: 0/22 (top: momentum_quality 65.8점, Sharpe=0.73, PF=1.17)
- Paper Sim SOL: 누락 (script 출력 확인 필요)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (narrow_range 87.1점, PF=1.83, std=5.18)

### 주요 코드 변경 이력 (Cycle 261)
1. `src/risk/drawdown_monitor.py` — set_atr_state(), get_atr_vol_multiplier(), DrawdownStatus.atr_vol_multiplier
2. `src/ml/features.py` — atr_vol_regime 피처 추가, feature_names 18→19개
3. `tests/test_feature_builder.py` — test_returns_18_base_features → test_returns_19_base_features
