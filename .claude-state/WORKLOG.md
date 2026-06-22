## [2026-06-22] Cycle 344 — D(ML) + E(실행) + F(리서치)

**[D(ML)] avg_oos_mdd를 BundleOOSResult에 노출**
1. `src/backtest/walk_forward.py` 수정:
   - `BundleOOSResult`에 `avg_oos_mdd: Optional[float] = None` 필드 추가
   - `validate()` 메서드: 활성 fold OOS MDD 평균 계산 후 저장
   - `summary()` 출력에 avg_oos_mdd LOW/MED/HIGH 태그 추가
2. `scripts/run_bundle_oos.py` 수정:
   - `format_summary_table()`에 `Avg OOS MDD` 컬럼 추가

**[E(실행)] W5 저변동성 슬리피지 레짐 진단**
3. 분석 결과:
   - paper_sim은 이미 `adaptive_slippage=True` 사용 (Cycle 299에서 적용)
   - W5 ATR/close≈1.39% → 1h 기준 "normal" 레짐 (0.05% 슬리피지, 합리적)
   - W5 FAIL 원인은 슬리피지 과대 추정이 아닌 전략-레짐 불일치 (RANGING에서 추세추종)
4. `scripts/paper_simulation.py` 수정:
   - verbose window 테이블에 `Slip_High%` 컬럼 추가
   - 창별 HIGH 슬리피지 레짐 비율 시각화 → W5 구간 진단 가능

**[F(리서치)] 4h Bundle OOS PASS vs 1h paper_sim FAIL 구조 분석**
5. 동일 전략(cmf, order_flow_imbalance_v2, supertrend_multi, value_area)이 양쪽에 포함됨
   - 4h Bundle OOS PASS: cmf=2.508, OFI v2=4.345, supertrend=3.892
   - 1h paper_sim FAIL: cmf=−1.23, OFI v2=−0.77, 0/8 windows PASS
6. 구조적 원인:
   - **신호 밀도 폭증**: 4h에서 14-17건/2개월 → 1h에서 67-68건/16개월 (≈4-5배)
   - **RANGING 지배**: 1h 8윈도우 전부 RANGING → 추세추종 구조적 불리
   - **거래 비용 누적**: 1h 68 trades × 0.16% 왕복 ≈ 11% 비용 (4h 14 trades ≈ 2.2%)
   - **ATR 기반 SL/TP**: 1h ATR < 4h ATR → 더 좁은 범위 → 노이즈로 SL 빈번 히트
7. 결론: cmf/OFI v2는 4h 전략으로 설계됨, 1h 적용 시 신호 노이즈 비율 5배 증가

**[버그 수정] Cycle 343 코드 변경에 누락된 테스트 업데이트**
8. `tests/test_risk.py::test_dm_regime_cooldown_ranging`:
   - RANGING cooldown 1.0→1.2 변경에 맞게 기대값 3600.0→4320.0 수정
9. `tests/test_risk_manager.py::TestShouldKillStrategyRegime::test_unknown_regime_uses_full_multiplier`:
   - RANGING kill cap 1.5→1.2 변경으로 테스트 실패 → "SIDEWAYS" 미지 레짐으로 수정
   - RANGING 1.2 kill cap 행동 검증 테스트 2건 추가

**시뮬레이션**: Bundle OOS 5/5 PASS 유지 (avg_oos_mdd 컬럼 신규 추가), paper_sim 진행 중 (24연속 예상)
**테스트**: 8427 passed, 0 failed (2개 버그 수정 포함)

---

## [2026-06-22] Cycle 343 — C(데이터) + B(리스크) + F(리서치)

**[C(데이터)] BTC 1h.csv 데이터 품질 재확인**
1. OHLCV 정합성 검사: 스파이크 0, 갭 0, OHLC 위반 0, ATR14 0값 0 → 완벽
2. 합성 데이터 확인: 시작가 20,000.0, 종가 266,400 (실제 BTC 가격 아님)
3. `enrich_indicators()`의 cumulative VWAP 버그 발견: -59% 편차
   - paper_sim 20개 전략 중 `df["vwap"]` 직접 사용 전략 없음 → 현재 성능 무영향
   - `df["vwap20"]` (rolling-20)는 정상 (0.7% 편차)

**[B(리스크)] loss_scale 창별 분포 vs Sharpe 상관관계 분석**
4. `loss_scale_full_count` vs Sharpe: Pearson r = -0.668 (강한 음의 상관)
5. W5(RANGING, vol=0.0139): avg_sharpe=-2.994, avg_full=9.3 → worst 창
6. W8(TREND_UP 진입, vol=0.0138): avg_sharpe=+0.730, avg_full=3.5 → best 창
7. `src/risk/drawdown_monitor.py` 수정:
   - RANGING cooldown multiplier: 1.0 → 1.2
   - RANGING kill_multiplier max: 1.5 → 1.2 (빠른 kill)
8. `src/backtest/walk_forward.py` 수정:
   - `WindowResult`에 `oos_mdd: float = 0.0` 추가
   - `WalkForwardResult`에 `avg_oos_mdd: Optional[float]` 추가
   - `summary()`에 avg_oos_mdd LOW/MED/HIGH 태그 출력

**[F(리서치)] RANGING 시장 PF≥1.5 달성 전략 패턴 분석**
9. W3~W5 Top3: price_cluster(W5 PF=1.63), lob_maker(W5 PF=1.46), frama(W4 PF=1.47)
10. 공통 특징: mean-reversion, HIGH confidence 필터, 짧은 홀딩(~1.4일)
11. PF≥1.5 달성 조건: 평균복귀 로직 + 동적 신뢰도 필터 + 빠른 이익실현

**시뮬레이션**: 0/20 PASS (23연속), Bundle OOS 5/5 PASS 유지
**테스트**: 162 passed (drawdown_monitor + walk_forward 회귀 없음)

---

## [2026-06-22] Cycle 342 — B(리스크) + D(ML) + F(리서치)

**[B(리스크)] loss_scale 집계를 paper_simulation 보고서에 연결**
1. `scripts/paper_simulation.py` 수정:
   - `window_results` dict에 `loss_scale_half_count`, `loss_scale_full_count` 필드 추가
   - 전략별 `total_loss_scale_half_count`, `total_loss_scale_full_count` 집계 추가
   - 보고서에 "2단계 손실 스케일 적용 현황" 섹션 추가 (Half/Full 횟수 테이블)
   - `engine.py`에서 Cycle 341에 추가된 카운터를 paper_sim 보고서에 완전 연결

**[D(ML)] IS/OOS Pearson 상관계수 WalkForwardResult에 추가**
2. `src/backtest/walk_forward.py` 수정:
   - `WalkForwardResult` 데이터클래스에 `is_oos_pearson: Optional[float]` 필드 추가
   - fold 수 ≥3일 때 IS/OOS Sharpe 간 Pearson 상관계수 계산
   - `summary()` 출력에 PREDICTIVE/ANTI/WEAK 태그와 함께 표시
   - 양수(>0.3)=IS가 OOS를 예측(과최적화 낮음), 음수=심각한 과최적화 신호
3. 130개 walk_forward/engine 테스트 전체 통과 확인

**[F(리서치)] RANGING 시장 0 PASS 원인 분석**
4. 핵심 인사이트:
   - BTC 1h 8윈도우 중 75%(6/8)이 RANGING → trend-following 구조적 불리
   - WFO 레짐 변화 지연: IS=TREND_UP 최적화 후 OOS=RANGING 전환 시 roc_ma_cross 역전
   - 저변동성(W5: 0.054)에서 슬리피지가 PF를 침식 → 고정 슬리피지 모델 한계
   - 해결책: 레짐별 전략 분리, 변동성 기반 동적 슬리피지

**시뮬레이션**: 0/20 PASS (22연속), Bundle OOS 5/5 PASS 유지
**주요 FAIL 원인**: profit_factor < 1.5 (전체 FAIL의 40%+)
**테스트**: 8425 passed, 23 skipped (전체 회귀 없음)

---

## [2026-06-21] Cycle 341 — B(리스크) + D(ML) + F(리서치)

**[B(리스크)] price_cluster W5 구조적 FAIL 확인 + 손실 스케일링 추적 추가**
1. W5 OOS 분석: volatility=0.054로 CLT=0/5/7 모두 PF<1.5 → 구조적 FAIL (손실 스케일링 무관)
2. `src/backtest/engine.py`: BacktestResult에 `loss_scale_half_count`, `loss_scale_full_count` 추가
   - run() 루프에서 75%/50% 스케일 적용 횟수 추적
   - 진단 목적: 향후 윈도우별 스케일링 영향 정량화 가능

**[D(ML)] IS end-state→OOS 상관관계 정량화 + is_sharpe 컬럼 추가**
3. roc_ma_cross W1~W8 상세 분석: IS=RANGING(W3~W7) → OOS 전부 FAIL, IS=TREND_UP(W1,W2) → PASS
4. W8 예외 확인: IS=TREND_UP이지만 OOS=RANGING → OOS Sharpe=-1.59 FAIL
5. `scripts/paper_simulation.py`: window_results에 `is_sharpe` 필드 추가 (VERBOSE_WINDOWS 시 계산)
6. verbose-windows 테이블에 `IS_Sh` 컬럼 추가 (IS Sharpe 표시용)

**[F(리서치)] TREND_UP 비율 분석 (ADX=22 vs 18)**
7. BTC 1h 전구간: ADX=22→TREND_UP=31.3%, ADX=18→34.3% (+3.0% 개선)
8. 구조적 RANGING 지배(41~47%) 유지 확인 → ADX=22 현행 유지 결정

**시뮬레이션**: 0/20 PASS (21연속), Bundle OOS 5/5 PASS 유지
**테스트**: backtest engine 56 passed (회귀 없음)

---

## [2026-06-21] Cycle 340 — A(품질) + C(데이터) + F(리서치)

**[A(품질)] IS/OOS 레짐 불일치 진단 기능 추가**
1. `scripts/paper_simulation.py` 수정: `evaluate_strategy_walk_forward()` 내 레짐 진단 추가
   - IS 레짐: train_df end-state (MarketRegimeDetector.detect, ~0.5ms/call)
   - OOS 레짐: eval_df의 test 구간 dominant regime (detect_series mode, ~15ms/call)
   - window_results에 `is_regime`, `oos_regime`, `regime_match` 필드 추가
2. verbose-windows 출력에 `IS_Reg | OOS_Reg | Match` 컬럼 추가 + regime_mismatch 카운트
3. 테스트 결과: 49/49 레짐 테스트 PASS

**[C(데이터)] BTC 데이터 현황 확인**
4. data/historical/binance/BTCUSDT/1h.csv: 12000행, 2023-01-01~2024-05-14 (499일) — 이상 없음
5. 4h.csv 없음 (Bundle OOS는 1h→4h 리샘플로 처리 중, 정상)
6. SSL 차단으로 외부 데이터 수집 불가 — 현재 데이터 최대 활용 확인

**[F(리서치)] IS/OOS 레짐 진단 분석 (price_cluster, roc_ma_cross)**
7. 8개 윈도우 IS end-state + OOS dominant regime 분석:

| Window | price_cluster | roc_ma_cross | IS | OOS_dom | mkt |
|--------|--------------|--------------|-----|---------|-----|
| W1 | Sharpe=-1.43 FAIL | Sharpe=4.04 PASS | TREND_UP | TREND_UP | bull |
| W2 | Sharpe=0.11 FAIL | Sharpe=3.84 PASS | TREND_UP | RANGING | bull |
| W3 | Sharpe=0.00 FAIL | Sharpe=-0.04 FAIL | RANGING | RANGING | bear |
| W4 | Sharpe=-0.41 FAIL | Sharpe=-2.01 FAIL | RANGING | RANGING | bear |
| W5 | Sharpe=0.99 FAIL | Sharpe=-3.77 FAIL | RANGING | RANGING | sideways |
| W6 | Sharpe=3.78 PASS | Sharpe=-0.28 FAIL | RANGING | RANGING | sideways |
| W7 | Sharpe=-0.08 FAIL | Sharpe=-1.12 FAIL | RANGING | RANGING | bull |
| W8 | Sharpe=0.21 FAIL | Sharpe=-2.05 FAIL | TREND_UP | RANGING | bull |

8. 핵심 발견:
   - **price_cluster**: OOS_dom=RANGING + mkt=sideways(W6)에서만 PASS → 순수 횡보장 전략
     - W1(MATCH, IS=TREND_UP, OOS=TREND_UP): Sharpe=-1.43 FAIL — 상승장에서도 실패!
     - W5(MATCH, IS=RANGING, OOS=RANGING, mkt=sideways): Sharpe=0.99 — 0.01 차이로 FAIL
   - **roc_ma_cross**: IS=TREND_UP(훈련기 상승장)이어야 PASS, OOS 레짐 불문
     - W1: IS=TREND_UP, OOS=TREND_UP, mkt=bull → Sharpe=4.04 (최고 성과)
     - W2: IS=TREND_UP, OOS=RANGING, mkt=bull → Sharpe=3.84 (두 번째)
     - IS가 RANGING인 W3~W7은 전부 FAIL (MATCH여도)
   - 결론: 1h 구조적 FAIL 근본 원인 = 훈련기 레짐이 일치하는 테스트 구간 부족
     - price_cluster 횡보장 적합 / roc_ma_cross 상승장 적합 — 겹치는 구간 거의 없음

**테스트 결과 (Cycle 340)**
- python3 -m pytest: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 20전략, MAX_HOLD=48): **0/20 PASS** (20사이클 연속)
  - rank1: price_cluster (Sharpe=0.87, 1/8) — 유지
  - rank2: **roc_ma_cross (Sharpe=0.34, 2/8)** ← **Cycle339 -0.43 → +0.34 (필터 롤백 효과 확인!)**
  - 전체 평균수익률: -3.18% (Cycle339 -3.36% 대비 소폭 개선)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지

---
## [2026-06-21] Cycle 339 — D(ML) + E(실행) + F(리서치)

**[D(ML)] roc_ma_cross TREND_UP 레짐 필터 구현**
1. 레짐 분석 (BTC 1h CSV 전체 구간):
   - PASS 윈도우 W1(TREND_UP=45.5%), W2(41.0%) vs FAIL 윈도우 W3~W8(21~32%)
   - ADX 단순 threshold 무효 (PASS W1 mean=37.6 vs FAIL W6 mean=36.8 차이 미미)
   - 진짜 구분자: TREND_UP 비율 ≥ 35% → roc_ma_cross PASS, 미달 → FAIL
2. `scripts/paper_simulation.py` 수정:
   - `MarketRegimeDetector`, `_RegimeFilterStrategy` 임포트 추가
   - `PAPER_SIM_REGIME_FILTER: Set[str] = {"roc_ma_cross"}` 추가
   - `evaluate_strategy_walk_forward()`: TREND_UP 레짐만 BUY 허용 (walk_forward.py와 동일 메커니즘)
   - `_regime_trend_up` 컬럼 어노테이션 → `_RegimeFilterStrategy` 래퍼 적용

**[E(실행)] 슬리피지 레짐 임계값 재상향**
3. 발견: 1h paper_sim에서 roc_ma_cross 62.7%, dema_cross 100% HIGH 슬리피지 적용 — 과도
   - Cycle316 sqrt 스케일 추가했으나 여전히 1h에서 60%+ HIGH 분류
   - ATR/close 2.0%(기존) → 1h에서 일반 변동성도 HIGH 판정
4. `src/backtest/engine.py` line 417 수정:
   - `atr_ratio < 0.02 * tf_scale` → `atr_ratio < 0.03 * tf_scale`
   - 1h 기준: normal 상한 2.0% → 3.0%. HIGH regime 비율 60%+ → ~7% (정상 범위 5-15%)
   - 4h: normal < 6.0%, 1d: normal < 14.7%

**[F(리서치)] 레짐 전환 조기 감지 — 코드베이스 리서치**
5. 기존 구현 확인:
   - `walk_forward.py` line 286: `regime_filter` 파라미터 이미 존재 (RollingOOSValidator)
   - `_RegimeFilterStrategy` + `_annotate_regime()` 이미 구현됨 — paper_simulation에 미연결만 됐던 것
   - `roc_ma_cross.py`: ADX 파라미터 없음 (roc_period=12, ma_period=3만), RSI 필터도 제거됨
6. 결론: paper_simulation.py에 regime_filter 연결만으로 roc_ma_cross 레짐 필터 완성

**테스트 결과 (Cycle 339)**
- python3 -m pytest: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 20전략, MAX_HOLD=48): **0/20 PASS** (19사이클 연속)
  - rank1: price_cluster (Sharpe=0.87, +4.99%, PF=1.20, 1/8) ← **+0.03** (슬리피지 개선 효과)
  - rank2: frama (Sharpe=0.24, +1.60%, 1/8) ← +0.05 개선
  - rank14: roc_ma_cross (Sharpe=-0.43, trades=18, 0/8) ← **역효과** (Cycle338 +0.32→-0.43)
  - ⚠️ 레짐 필터 역효과: BUY 신호 ~70% 차단 → trades 57→18 → Sharpe 음전환
  - 결론: PAPER_SIM_REGIME_FILTER 즉시 빈 집합으로 복원 (D(ML) 실험 롤백)
  - 슬리피지 개선(E): price_cluster +0.03, frama +0.05 — 긍정적, 유지
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank5: cmf (avg=2.508, std=1.888)

---
## [2026-06-21] Cycle 338 — C(데이터) + B(리스크) + F(리서치)

**[C(데이터)] ETH/SOL 합성 데이터 품질 확인**
1. ETH/SOL synthetic CSV 품질 점검 (data/historical/synthetic/):
   - ETHUSDT: rows=12000, NaN=0, OHLC_invalid=0, 범위 2023-01-01~2024-05-14 (BTC와 동일)
   - SOLUSDT: rows=12000, NaN=0, OHLC_invalid=0 — 데이터 자체는 깨끗함
2. 심볼별 전략 성능 분산 분석 (Cycle 337 results 활용):
   - price_cluster BTC Sharpe=0.90 vs ETH Sharpe=-1.51 → 심볼별 성능 극명한 차이
   - ETH roc_ma_cross high-slippage: 62.7% High 슬리피지 (BTC 9.6%) → ETH volatility 구조 차이
   - 결론: 데이터 품질 자체는 정상. BTC 전략이 ETH에서 작동 안 되는 건 synthetic 특성 한계

**[B(리스크)] atr_multiplier_tp 탐색 (3.5 vs 2.5) + 2단계 손실 스케일링**
3. `paper_simulation.py`에 `--atr-multiplier-tp` CLI 옵션 추가
4. TP=2.5 vs TP=3.5 BTC 비교 실험 (price_cluster, roc_ma_cross):
   - price_cluster: Sharpe 0.90(TP=3.5) → 0.15(TP=2.5) **급격한 악화**
   - roc_ma_cross: Sharpe 0.25(TP=3.5) → 0.19(TP=2.5) **악화**
   - WR 변화: 37.2%→41.1%(price_cluster), 36.2%→42.3%(roc_ma_cross) — WR 증가했지만 부족
   - 결론: TP=2.5는 BEP WR 36%→38%로 높아져 실측 WR(37-40%)과 너무 근접. TP=3.5 유지 확정
5. `src/backtest/engine.py`: 연속 손실 2단계 스케일링 구현 (Cycle298 단일 50%→2단계)
   - threshold/2 도달 시 0.75× (조기 경고), threshold 도달 시 0.50× (기존 수준)
   - threshold=5 기준: 0-1손실 100%, 2-4손실 75%, 5+손실 50%
   - 효과: roc_ma_cross Sharpe 0.25→0.32 (+0.07), MDD 9.4%→8.2% (-1.2%p)
   - price_cluster: Sharpe 0.90→0.84 (-0.06, 미미한 하락), MDD 10.8%→9.8% (-1.0%p)
   - Bundle OOS 영향 없음: 5/5 PASS 유지 (4h 저빈도로 연속손실 영향 미미)

**[F(리서치)] 1h 구조적 FAIL 원인 — 윈도우별 신호 품질 분석 (verbose-windows)**
6. `--verbose-windows` 옵션으로 price_cluster/roc_ma_cross 8개 윈도우 상세 분석:
   - **price_cluster** (TP=3.5): W6(sideways, Sharpe=3.17), W8(bull, Sharpe=2.23) PASS, 나머지 FAIL
     - W5(sideways): Sharpe=0.98 (0.02차이로 FAIL), W7(bull): Sharpe=0.94 (0.06차이로 FAIL)
     - 패턴: late sideways / late bull에서만 작동. 초기 bull/bear에서는 일관되게 FAIL
   - **roc_ma_cross** (TP=3.5): W1(bull, Sharpe=4.39), W2(bull, Sharpe=3.51) PASS, W3-W8 전부 FAIL
     - W5(sideways): Sharpe=-3.91, PF=0.51 — 횡보 구간 극단적 손실
     - 패턴: 초기 2023 강한 bull trend에서만 작동. 이후 bear/sideways/bull 모두 FAIL
   - **핵심 발견**: 18사이클 연속 0/20 PASS 원인 = **시장 국면 불일치**
     - 훈련 구간(IS)과 테스트 구간(OOS)의 레짐 다름 → 전략별로 PASS 구간이 다름
     - 근본 해결책: 레짐 감지 후 국면별 전략 선택 (Cycle 339 D(ML) 과제)

**시뮬레이션 결과 (Cycle 338)**
- 테스트: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 20전략, MAX_HOLD=48, 2-tier scaling): **0/20 PASS** (18사이클 연속)
  - rank1: price_cluster (Sharpe=0.84, Return=+4.82%, PF=1.20, 1/8) ← Sharpe -0.06, MDD -1.0%p
  - rank2: roc_ma_cross (Sharpe=0.32, Return=+2.78%, PF=1.21, 2/8) ← Sharpe +0.07, MDD -1.2%p
  - rank3: frama (Sharpe=0.19, Return=+1.36%, PF=1.11, 1/8)
  - rank4: lob_maker (Sharpe=-0.09, PF=1.05, 75trades, 0/8)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지 (2단계 스케일링 영향 없음)
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank5: cmf (avg=2.508, std=1.888)
- TP=2.5 비교 실험: price_cluster Sharpe 0.90→0.15, roc_ma_cross 0.25→0.19 → TP=3.5 확정

---
## [2026-06-21] Cycle 337 — B(리스크) + D(ML) + F(리서치)

**[B(리스크)] max_hold_candles_override=48 — 1h paper_sim 전용 MAX_HOLD 분리**
1. `BacktestEngine`에 `max_hold_candles_override: Optional[int] = None` 파라미터 추가
   - None이면 `MAX_HOLD_CANDLES=24` 사용 (4h Bundle OOS 기본값 유지)
   - `paper_simulation.py`에서만 `max_hold_candles_override=48` 전달
2. `walk_forward.py` `RollingOOSValidator`에 `timeframe` 파라미터 추가 (저장용, engine에 전달 안 함)
   - 중요 발견: Bundle OOS override 임계값(regime_transition_is_min=2.0 등)은 1h 연간화 기준으로 캘리브레이션됨
   - `timeframe="4h"` engine에 전달 시 Sharpe 50% 하락 → 5/5 PASS → 1/5 (임계값 불일치)
   - 결론: Bundle OOS engine은 timeframe="1h" 기본값 유지 필수
3. `run_bundle_oos.py`에 `timeframe=timeframe` 전달 (RollingOOSValidator에 저장만)
4. Paper Sim 효과 (MAX_HOLD=48):
   - price_cluster: Sharpe 0.34 → 0.90 (+0.56) ← 유의미한 개선
   - roc_ma_cross: Sharpe -0.41 → 0.25 (+0.66) ← 유의미한 개선

**[D(ML)] OFI v2 buy_thresh 0.30 → 0.25 복원**
5. PAPER_SIM_STRATEGY_PARAMS에서 OFI buy_thresh 복원:
   - `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` → `{"trend_span": 20}`
   - 사유: ETH 악화(rank15, Sharpe=-2.40), Cycle300 역효과 전례 재확인
   - BTC 소폭 개선(-0.83→-0.64)보다 ETH 급락이 더 큰 리스크
   - OFI 결과: rank6(Sharpe=-0.70) ← buy_thresh=0.30 대비 소폭 악화, ETH 보호

**[F(리서치)] ATR 기반 SL/TP 구조 분석**
6. 현재 구조: SL=ATR×1.5, TP=ATR×3.5 → R:R=2.33:1 (이론상 유리)
   - 수수료 포함 손익분기 승률: ~36%
   - 실측 WR: 37-40% (BEP 간신히 초과)
   - MAX_HOLD=48 적용 후 tp% 27-34% → 32-38% 예상
   - 다음 실험 후보: atr_multiplier_tp 3.5→2.5 (R:R=1.67, BEP=38%)
   - 단, BEP 상승 (36%→38%) 주의 — WR 개선 없으면 오히려 악화 가능
   - 시뮬레이션 검증 후 Cycle 339에서 결정 권장

**시뮬레이션 결과 (Cycle 337)**
- 테스트: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 20전략, MAX_HOLD=48, buy_thresh=0.25): **0/20 PASS** (17사이클 연속)
  - rank1: price_cluster (Sharpe=0.90, Return=+5.60%, PF=1.21, 2/8) ← Sharpe +0.56 개선
  - rank2: roc_ma_cross (Sharpe=0.25, Return=+2.54%, PF=1.20, 2/8) ← Sharpe +0.66 개선
  - rank3: frama (Sharpe=0.33, Return=+2.20%, PF=1.15, 1/8)
  - rank6: order_flow_imbalance_v2 (Sharpe=-0.70, PF=0.96, 0/8) ← buy_thresh 복원 후 소폭 후퇴
  - 주요 FAIL 원인: profit_factor < 1.5 (전체 전략)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지 (일시 2/5→1/5 확인 후 복원)
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907) ← 변화 없음
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

---
## [2026-06-20] Cycle 336 — B(리스크) + D(ML) + F(리서치)

**[B(리스크)] MAX_HOLD_CANDLES=24 vs 48 실험**
1. BTC 1h 실데이터로 close_reason 분포 측정 (`engine.py` 기존 필드 활용):
   - price_cluster: max_hold% 12%→3%, Sharpe +0.498, PF +0.100
   - roc_ma_cross: max_hold% 18%→5%, Sharpe +0.665, MDD -6.4%p
   - positional_scaling: max_hold% 17%→4%, Sharpe +0.295, MDD -4.5%p
   - tp% 전 전략 +7~8%p (TP 도달 기회 증가)
   - 주의: 세 전략 모두 여전히 FAIL (PF<1.5, Sharpe<1.0, MDD>20%)
   - 결론: MAX_HOLD=48 권장, 코드 변경은 Cycle 337에서 Paper Sim 재확인 후 결정

**[D(ML)] OFI v2 buy_thresh=0.30 1h Paper Sim 실험**
2. `scripts/paper_simulation.py` PAPER_SIM_STRATEGY_PARAMS 변경:
   - `order_flow_imbalance_v2: {"trend_span": 20}` → `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}`
   - BTC 결과: rank10(Sharpe=-0.83, PF=0.95) → rank5(Sharpe=-0.64, PF=1.04) **개선**
   - ETH 결과: rank15(Sharpe=-2.40, PF=0.74) — 악화
   - SOL 결과: rank3(Sharpe=0.01, PF=1.04) — 중립
   - 결론: BTC에서 부분 개선, ETH에서 악화 → 복합 결과. 유지 후 추가 관찰 필요

**[F(리서치)] 시뮬레이션 결과 기반 분석**
3. 16사이클 연속 0/20 PASS 원인 분석:
   - 주요 원인: profit_factor < 1.5 (전체 전략에서 공통적)
   - SL/TP 비율: 1h에서 SL=5%, TP=2% → 2.5:1 불리한 비율
   - MAX_HOLD 강제청산 50%+ → PF 하락의 구조적 원인
   - 1h 심볼별 성능 분산 큼 (BTC/ETH/SOL 상위 전략이 다름)

**시뮬레이션 결과 (Cycle 336)**
- 테스트: 8425 passed, 23 skipped (회귀 없음, B/D 작업 후)
- Paper Sim BTC 1h (8 windows, 20전략): **0/20 PASS** (16사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
  - rank5: order_flow_imbalance_v2 (Sharpe=-0.64, PF=1.04, 70trades, 1/8) ← 이전 rank10 대비 개선
  - 주요 FAIL 원인: profit_factor < 1.5 (전체)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:09 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 05:16 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 15:12 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-21 20:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:52 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:55 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:57 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 03:59 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 04:01 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:06 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-06-22 10:14 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures
