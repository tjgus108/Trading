# Current Cycle Briefing

_Cycle 261 — 2026-06-02_
_카테고리: B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): DrawdownMonitor ATR 변동성 필터 추가
- `src/risk/drawdown_monitor.py`:
  - `set_atr_state(atr, atr_ma, threshold=1.5)` 메서드 추가
    - ATR > ATR_MA * 1.5 이면 `_atr_vol_mult = 0.5` (포지션 사이즈 50% 자동 축소)
    - 정상화 시 `_atr_vol_mult = 1.0` 복원
  - `get_atr_vol_multiplier()` 조회 메서드 추가
  - `get_size_multiplier()`: `min(streak_mult, mdd_mult, atr_vol_mult)` 삼중 최소값 적용
  - `DrawdownStatus` 데이터클래스에 `atr_vol_multiplier: float = 1.0` 필드 추가
  - `reset()` 시 ATR 상태 초기화 포함
- 근거: CMF/momentum 전략이 고변동성 구간(ATR 급등 시)에서 일관되게 실패
  → 리스크 레이어에서 포지션 사이즈를 직접 억제하여 MDD 방어

### D(ML): FeatureBuilder atr_vol_regime 피처 추가
- `src/ml/features.py`:
  - `atr_vol_regime` 피처 추가: ATR_pct > ATR_MA50 * 1.5 이면 1.0, 아니면 0.0
  - 기본 피처 목록 18 → **19개** (feature_names)
  - REGIME_FEATURE_CONFIG `bull` 리스트에 `atr_vol_regime` 추가
- `tests/test_feature_builder.py`: 피처 수 카운트 테스트 18 → 19로 수정
- 근거: momentum_quality가 고변동성 구간 진입 조건을 ML로 학습 가능하도록
  DrawdownMonitor.set_atr_state()와 동일한 1.5x ATR 임계값으로 일관성 유지

### F(리서치): 시뮬레이션 기반 패턴 분석
- BTC supertrend_multi 2사이클 연속 1위 (Cycle 260: 67.6점 → 261: 86.6점↑)
  - trend-following 특성이 BTC에서 일관되게 우위 확인
  - Cycle 262 이후 supertrend_multi 파라미터 계열 집중 분석 권장
- mc_p_value > 0.05 실패가 가장 많은 공통 패턴
  - 거래 수 증가(신호 완화) 또는 신호 품질 향상이 핵심 과제
- ETH momentum_quality: PF=1.17 근-PASS (목표 1.5) → atr_vol_regime 피처로 다음 사이클 재검증

## 시뮬레이션 결과 (Cycle 261)
- Paper Sim BTC 1h (실CSV): 0/22 PASS
  - Top: supertrend_multi (score=72.6, Return=+5.87%, Sharpe=0.43, PF=1.13)
  - 2위: price_cluster (score=69.2, Return=+2.50%)
- Paper Sim ETH (GARCH OU): 0/22 PASS
  - Top: momentum_quality (score=65.8, Sharpe=0.73, PF=1.17, MDD=10.4%, Consist=0/8)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS
  - Top: narrow_range (score=87.1, OOS Sharpe=0.24, OOS PF=1.83, std=5.18)

## 테스트: 8369 passed, 23 skipped (변경 없음)

## 다음 Cycle 262 (262 mod 5 = 2 → B+D+F)
- B: RiskManager.check()에서 DrawdownMonitor.set_atr_state() 연계 구현
  - src/risk/manager.py의 check() 메서드에 ATR MA 전달 로직 추가
- D: atr_vol_regime 피처의 momentum_quality 성과 개선 효과 검증
  - SOL 시뮬레이션 결과 누락 확인 → scripts/paper_simulation.py SOL 재실행
- F: BTC supertrend_multi 2연속 1위 → 파라미터 계열 상세 분석
