# Current Cycle Briefing

_Cycle 344 | 2026-06-22 | D(ML) + E(실행) + F(리서치)_

## 완료된 사이클: 344
**카테고리**: D(ML) + E(실행) + F(리서치)

### D(ML): avg_oos_mdd를 BundleOOSResult에 노출

**작업**:
- `src/backtest/walk_forward.py` - `BundleOOSResult`에 `avg_oos_mdd: Optional[float] = None` 추가
  - `validate()` 메서드에서 활성 fold의 OOS MDD 평균 계산
  - `summary()` 출력에 LOW/MED/HIGH 태그 추가
- `scripts/run_bundle_oos.py` - `format_summary_table()`에 `Avg OOS MDD` 컬럼 추가

**결과**: Bundle OOS 리포트에 avg_oos_mdd 컬럼 추가 확인
- cmf: 5.19%, order_flow_imbalance_v2: 3.36%, supertrend_multi: 2.23%, vwap_cross: 2.67%, value_area: 1.87%

### E(실행): W5 저변동성 슬리피지 레짐 진단

**분석 결과**:
- paper_sim은 이미 `adaptive_slippage=True` 사용 (Cycle 299에서 적용)
- W5 ATR/close ≈ 1.39% → 1h 기준 임계값: low<0.5%, normal<3.0%
- W5는 "normal" 레짐 (0.05% 슬리피지) → 슬리피지 모델 과대 추정 아님
- W5 FAIL 원인: 슬리피지가 아닌 전략-레짐 불일치 (RANGING에서 추세추종)

**코드 개선** — `scripts/paper_simulation.py`:
- VERBOSE_WINDOWS 테이블에 `Slip_High%` 컬럼 추가
- 창별 HIGH 슬리피지 레짐 비율 시각화 → W5 구간 진단 가능

### F(리서치): 4h Bundle OOS PASS vs 1h paper_sim FAIL 구조 분석

**발견**:
- cmf, order_flow_imbalance_v2, supertrend_multi, value_area는 양쪽 테스트에 포함됨
- 4h Bundle OOS: cmf=2.508, OFI v2=4.345, supertrend=3.892 → 5/5 PASS
- 1h paper_sim: cmf=-1.23, OFI v2=-0.77, supertrend=미포함 → 0/8 PASS

**구조적 원인** (4가지):
1. **신호 밀도 4-5배 증가**: 4h 14-17 trades/fold → 1h 67-68 trades → 노이즈 비율 폭증
2. **RANGING 지배**: 1h 8개 윈도우 전부 RANGING → 추세추종 구조적 불리
3. **거래비용 누적**: 1h 68×0.16% ≈ 11% vs 4h 14×0.16% ≈ 2.2%
4. **ATR 기반 SL/TP 좁아짐**: 1h ATR < 4h ATR → 노이즈로 SL 빈번 히트

**결론**: cmf/OFI v2는 4h 타임프레임 전략. 1h에서 신호 노이즈 비율 5배 증가는 구조적 한계

### 버그 수정 (Cycle 343 코드 변경 후 누락된 테스트 업데이트)

- `tests/test_risk.py::test_dm_regime_cooldown_ranging`:
  - RANGING cooldown 1.0→1.2 변경에 맞게 기대값 3600.0→4320.0 수정
- `tests/test_risk_manager.py::test_unknown_regime_uses_full_multiplier`:
  - RANGING kill cap 1.5→1.2로 변경되어 테스트 실패
  - "SIDEWAYS" 미지 레짐으로 수정 + RANGING 1.2 cap 검증 테스트 2건 추가

## 시뮬레이션 결과

### Paper Simulation (1h, 8-fold, BTC only)
- **PASS: 0/20** (24연속)
- Top: price_cluster (Sharpe=0.87, 1/8), roc_ma_cross (Sharpe=0.34, 2/8)
- 주요 FAIL: profit_factor < 1.5

### Bundle OOS (4h, BTC/USDT)
- **PASS: 5/5** ✅ (유지)
- avg_oos_mdd 컬럼 신규: cmf=5.19%, OFI v2=3.36%, supertrend=2.23%, vwap=2.67%, value_area=1.87%
- #1 order_flow_imbalance_v2 (Score=62.0, OOS Sharpe=4.345, std=0.907)

## 테스트 결과

- **8427 passed, 0 failed** (버그 수정 2건 포함)

## 다음 사이클 (345) 방향

345 mod 5 = 0 → **A(품질) + C(데이터) + F**

1. A(품질): BundleOOSResult avg_oos_mdd 테스트 추가, RANGING 테스트 동기화 점검
2. C(데이터): cumulative VWAP → rolling VWAP 교체 영향 평가
3. F(리서치): cmf 1h 신호 노이즈 감소 — min_hold_bars=4 실험 설계
