# Next Steps

_Last updated: 2026-04-18 (Cycle 154 B완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 155
- 155 mod 5 = 0 → **C(데이터) + D(ML) + E(실행)** 패턴

### ✅ Cycle 154 완료 사항 (B: 리스크)

#### B(리스크): DrawdownMonitor 연속 손실 쿨다운 ✅ COMPLETE
- `src/risk/drawdown_monitor.py` — `streak_cooldown_seconds` 파라미터 추가 (기본 14400s = 4시간)
- `loss_streak_threshold` 도달 시 쿨다운 자동 시작 (기존: 50% 사이즈 축소만)
- 단일 손실 쿨다운보다 streak 쿨다운이 길면 streak 쿨다운 우선 적용
- `streak_cooldown_seconds=0` 설정으로 비활성화 가능
- `to_dict/from_dict` 직렬화 지원
- 5개 단위 테스트 추가 (tests/test_risk.py: 32 → 37 PASS)

### ✅ Cycle 153 완료 사항 (E: 실행)

#### E(실행): AccuracyDriftMonitor + DriftMonitor → live_paper_trader 연동 ✅ COMPLETE
- `scripts/live_paper_trader.py`에 두 모니터 임포트/초기화
- `AccuracyDriftMonitor`: symbol별 ML 예측 정확도 추적, `should_retrain=True` 시 `_weekly_retrain()` 즉시 호출 + `reset_detectors()`
- `DriftMonitor`: 거래 PnL% 스트리밍, `on_drift` 콜백으로 `CircuitBreaker._triggered=True` 강제 세팅
- 로깅: "Drift detected, triggering emergency retrain [symbol]"
- dry-run 검증 통과 (import OK, init OK)
- 기존 153 PASS 테스트 영향 없음 (pre-existing yaml 오류 외)

### ✅ Cycle 152 완료 사항

#### B(리스크): DriftMonitor — Page-Hinkley 드리프트 감지 ✅ COMPLETE
- src/risk/drawdown_monitor.py에 DriftMonitor 클래스 추가
- Page-Hinkley 테스트 (양방향: 평균 하락/상승 감지)
- 롤링 분산 비율 감지 (var_ratio_threshold 배 초과 → WARNING)
- DriftState enum: NORMAL / WARNING / DRIFT
- on_drift 콜백으로 CircuitBreaker 연동 가능
- 7개 단위 테스트 추가 (tests/test_risk.py: 25 → 32 PASS)

### ✅ Cycle 151 완료 사항

#### A(품질): SignalCorrelationTracker 테스트 추가 ✅ COMPLETE
- tests/test_risk.py에 8개 단위 테스트 추가 (25 total, 모두 PASS)
- 전체 테스트: 6682 passed, 20 failed (pre-existing 변화 없음)

#### C(데이터): ML 재학습 스케줄러 + Triple Barrier 레이블링 ✅ COMPLETE
- **주 1회 ML 재학습 훅** (`scripts/live_paper_trader.py`):
  - `WEEKLY_RETRAIN_INTERVAL = 7 * 24 * 3600` 상수 추가
  - `_last_retrain_time` 상태 변수 추가
  - `tick()` 내부에서 weekly 경과 시 `_weekly_retrain()` 자동 호출
  - `_weekly_retrain()`: BTC/ETH/SOL 각각 auto_retrain() → PASS 시 ml_models 캐시 갱신
  - `--ml-filter` 활성화 시에만 동작 (불필요한 API 호출 방지)
- **Triple Barrier 레이블링** (`src/ml/features.py`):
  - `FeatureBuilder` 파라미터 추가: `triple_barrier=False`, `tb_tp_pct=0.02`, `tb_sl_pct=0.01`
  - `_compute_triple_barrier_labels()`: high/low 배리어 터치 감지 (look-ahead 없음)
  - 기본 forward_return 방식과 호환 (triple_barrier=False가 기본값)
  - 사용: `FeatureBuilder(binary=True, triple_barrier=True, tb_tp_pct=0.02, tb_sl_pct=0.01)`
  - 시간 초과(배리어 미도달) → NaN → dropna 자동 제거 (이전 방식과 동일)

### ✅ Cycle 150 완료 사항

#### D(ML): BTC 시차 피처 + 모델 재학습 ✅ COMPLETE (FAIL)
- btc_close_lag1 피처 구현 (ETH/SOL용)
- BTC/ETH/SOL 모두 FAIL — 2026-03~04 레짐 변화 구간
- 주 1회 재학습 스케줄러 필요

#### E(실행): 피처 통일 + 상관관계 트래커 ✅ COMPLETE
- get_ml_features → FeatureBuilder 사용 (14피처 통일)
- SignalCorrelationTracker 추가 (src/risk/manager.py)
- 슬리피지 0.001→0.05 (0.05%)

#### F(리서치): CPCV + 메타-라벨링 ✅ COMPLETE
- skfolio CombinatorialPurgedCV 무료 사용 가능
- Triple Barrier + 메타-라벨링 → Precision 개선 기대

### ✅ Cycle 149 완료 사항

#### C(데이터): PFI 피처 제거 + missing data 경고 ✅ COMPLETE
- rsi14, rsi_zscore, price_vs_vwap 제거 (17→14 피처)
- missing data > 5% WARNING 추가
- ⚠️ 기존 BTC 모델 17피처 → 14피처 기준 재학습 필요

#### B(리스크): Kelly 레짐 개선 + VaR 검증 ✅ COMPLETE
- TREND_DOWN 스케일 1.0→0.6, compute(regime=) API 추가
- VaR/CVaR 정확성 확인, 테스트 6개 추가

#### F(리서치): ETH/SOL 예측 + Online Learning ✅ COMPLETE
- ETH/SOL 실패 원인: 높은 변동성 + 내러티브 이벤트
- 개선: BTC 시차 피처, 레짐별 서브모델, River 온라인 학습

### ✅ Cycle 148 완료 사항 (요약)

#### E(실행): ML 모델 실제 생성 ✅ COMPLETE
- BTC PASS (val 65.4%, test 63.5%), ETH/SOL FAIL
- 모델 저장: models/BTC_USDT_20260418_*_rf_binary.pkl
- PFI: rsi14, rsi_zscore, price_vs_vwap → 제거 후보
- live_paper_trader 임포트/모델 로드 정상 확인
- ⚠️ python3 = 3.7 (SSL 손상), /usr/local/bin/python3.11 사용 필수

#### A(품질): 테스트 수정 + kurtosis 경고 ✅ COMPLETE
- 5개 실패 → 0개 실패 (146 passed, 3 skipped)
- data_utils: 거래소 검증, pickle 폴백 추가
- kurtosis < 2.0 WARNING 로깅 추가

#### F(리서치): 봇 실패패턴 + 논문 조사 ✅ COMPLETE
- 73% 봇 6개월 내 실패 (과적합, 레짐 무대응)
- 유망: DQN 전략 선택기, 레짐별 ML 분리, DC+Meta-Learning

#### 이전: 합성 데이터 GARCH(1,1) + Student-t 교체 ✅ COMPLETE
- **상태**: ✅ COMPLETE
- **배경**: 기존 정상분포 기반 합성 데이터는 첨도 0.51로 비현실적 → fat tails 부재
- **구현**:
  - `tests/conftest.py`:
    - `_generate_garch_returns()` — GARCH(1,1) + Student-t df=6 수익률 생성
    - `_generate_garch_prices()` — 로그 수익률 기반 가격 시계열
    - `sample_df` 픽스처: GARCH 기반으로 교체
    - `_make_df()` 헬퍼 함수: 기존 인터페이스 유지하면서 내부 로직 교체
  - GARCH 파라미터 (BTC 1h 기준):
    - omega=0.0001, alpha=0.08, beta=0.90 (합=0.98, 현실적)
    - Student-t df=6 (kurtosis ≈ 5.0, 암호화폐 시장 수준)
- **검증 완료**:
  - 첨도: 5.0+ (기존 0.51 → 10배 개선)
  - 극단값 분포: ±3σ 1.7% (정상분포 0.3% vs fat tails 재현)
  - 모든 테스트 통과 (test_strategy.py 10/10 PASS)

#### 작업 2: 데이터 품질 모니터링 로깅 추가 ✅ COMPLETE
- **상태**: ✅ COMPLETE
- **구현**:
  - `src/data/data_utils.py`:
    - `validate_data()` 메서드에 통계 로깅 추가
    - 로그 수익률 기반 첨도, 왜도 계산
    - DEBUG 레벨 로깅: `Data quality stats for {symbol} {timeframe}: kurtosis=X.XX, skewness=Y.YY`
  - `src/data/feed.py`:
    - `_fetch_fresh()` 메서드에 통계 계산 추가
    - INFO 레벨 로깅에 첨도, 왜도 포함:
      - `DataFeed: {symbol} {timeframe} — {candles} candles, {missing} missing, {anomalies} anomalies, kurtosis=X.XX, skewness=Y.YY`
  - scipy.stats 임포트 추가 (data_utils.py, feed.py)

### ✅ Cycle 150 완료 사항 (E: 실행)

#### E(실행): 피처 불일치 수정, 상관관계 트래커, 슬리피지 현실화 ✅ COMPLETE
- `get_ml_features()` → FeatureBuilder 사용 (14피처 통일)
- `SignalCorrelationTracker` → src/risk/manager.py 추가, live_paper_trader 통합
- slippage_pct: 0.001 → 0.05 (0.05% 현실적 슬리피지)
- ⚠️ 기존 BTC 모델(17피처) → 14피처 기준 재학습 필요 (--auto-retrain)

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**
- 1500+ 캔들: FAIL (레짐 변화로 패턴 소멸)
- 구현 방향: 최근 1000캔들 + 주 1회 재학습 + binary_threshold=0.01
- 라이브 연동: `--ml-filter` 옵션으로 활성화

#### 경로 2: 레짐 필터링
- RANGING (28%): 모든 전략 -3~-4 Sharpe → **거래 금지** ✅
- TREND_UP (8%): narrow_range Sharpe +1.25 → 조건부 활성화
- TREND_DOWN (17%): 대부분 음수 → 거래 금지

**완료:**
- ~~슬리피지 현실화~~: 0.1%
- ~~MIN_TRADES 조정~~: 15
- ~~MC Permutation gate~~: 500 perms, sign randomization, p<0.05
- ~~Regime Detection~~: ADX+EMA+ATR 벡터라이즈
- ~~CircuitBreaker 통합~~: live paper trader
- ~~실패 테스트 수정~~: 14개 → 0개
- ~~파라미터 최적화~~: grid search + WF (3 전략, BTC/ETH)
- ~~ML 2-class 모드~~: binary=True (UP/DOWN), threshold 1%
- ~~레짐별 성과 분석~~: 벡터라이즈 감지 + chunk 백테스트
- ~~live_paper_trader 레짐 필터~~: RANGING에서 시그널 무시 ✅
- ~~DataFeed 레짐 캐시~~: 간단한 TTL 캐시 추가 ✅
- ~~ML 자동 재학습 파이프라인~~ — `--auto-retrain` 플래그, models/retrain_log.json ✅
- ~~ML 시그널 예측 모드~~ — `--predict [--model-file path]` 플래그 ✅
- ~~ML 시그널 live 연동~~ — `--ml-filter` 옵션, 자동 모델 로드, 시그널 필터 ✅
- ~~TWAP 실행기 검증~~ — 기본 동작 정상, 안정성 개선 ✅
- ~~합성 데이터 GARCH 교체~~ — GARCH(1,1) + Student-t, kurtosis ≥ 5.0 ✅
- ~~데이터 품질 통계 로깅~~ — kurtosis, skewness 모니터링 ✅
- ~~레짐 기반 동적 포지션 사이징~~ — TREND_UP 1.3x, HIGH_VOL 0.3x, DD한도 연동 ✅
- ~~ML PFI 분석 자동화~~ — feature_importance JSON 저장 ✅
- ~~LSTM BooleanArray 수정~~ — pandas ExtensionArray 호환 ✅

**다음 구현 과제 (우선순위):**
1. ~~**ML 모델 실제 생성**~~ — ✅ DONE (Cycle 148)
2. ~~**PFI near-zero 피처 제거**~~ — ✅ DONE (Cycle 149-C)
3. ~~**Kelly Sizer 레짐 개선**~~ — ✅ DONE (Cycle 149-B)
4. ~~**BTC 14-피처 재학습 + BTC 시차 피처**~~ — ✅ DONE (Cycle 150-D)
5. ~~**Triple Barrier 레이블링**~~ — ✅ DONE (Cycle 151-C)
6. ~~**Triple Barrier 학습 옵션 (train_ml.py)**~~ — ✅ DONE (Cycle 152-D): --triple-barrier, --tb-tp, --tb-sl
7. ~~**Concept Drift Detector**~~ — ✅ DONE (Cycle 152-D): src/ml/drift_detector.py (PHT+CUSUM+AccuracyDriftMonitor)
8. ~~**CPCV 구현**~~ — ✅ DONE (Cycle 152-D): combinatorial_purged_cv() in trainer.py (sklearn 기반)
9. **AccuracyDriftMonitor → live_paper_trader 연동** — `_weekly_retrain()` 내 drift 감지 시 즉시 재학습 트리거
10. **Triple Barrier 실데이터 검증** — `--bybit --triple-barrier --binary` 로 BTC 학습 후 CPCV 결과 비교
11. **live_paper_trader 실제 운영** — `/usr/local/bin/python3.11 scripts/live_paper_trader.py --days 7 --ml-filter`
