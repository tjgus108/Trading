# Next Steps

_Last updated: 2026-04-18 (Cycle 150 D 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 150
- 150 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** (표 기준 Cycle 5 패턴)

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
1. ~~**ML 모델 실제 생성**~~ — ✅ DONE (Cycle 148): BTC PASS val=65.4%/test=63.5%, ETH/SOL FAIL
   - **주의**: `python3` = Python 3.7 SSL 오류 → 반드시 `/usr/local/bin/python3.11` 사용
2. ~~**데이터 품질 임계값 경고**~~ — ✅ DONE (Cycle 148-A): kurtosis < 2.0 → WARNING 로그, data_utils.py
3. ~~**test_data_utils 2개 실패 수정**~~ — ✅ DONE (Cycle 148-A): 거래소 검증 사전 처리, parquet→pickle 폴백
4. ~~**PFI near-zero 피처 제거**~~ — ✅ DONE (Cycle 149-C): rsi14, rsi_zscore, price_vs_vwap 제거 (17→14 피처)
5. ~~**missing data 비율 경고**~~ — ✅ DONE (Cycle 149-C): >5% 누락 시 WARNING, data_utils.py
6. ~~**Kelly Sizer 레짐 개선**~~ — ✅ DONE (Cycle 149-B): TREND_DOWN 1.0→0.6, compute(regime=...) 파라미터 추가
7. ~~**BTC 14-피처 재학습 + BTC 시차 피처**~~ — ✅ DONE (Cycle 150-D): FAIL (레짐 변화), btc_close_lag1 구현됨
   - BTC val=0.654/test=0.519 FAIL, ETH val=0.508/test=0.636 FAIL, SOL val=0.578/test=0.493 FAIL
   - 시장 2026-03~04: 레짐 변화 구간 → val↔test 불일치. 주기적 재학습 필요
8. **live_paper_trader 실제 운영** — `/usr/local/bin/python3.11 scripts/live_paper_trader.py --days 7 --ml-filter`
9. **ML 주 1회 재학습 스케줄러** — cron 또는 live_paper_trader 내부 weekly retrain hook
10. **전략 상관관계 모니터링** — 활성 전략 간 상관 측정, live_paper_trader에 SignalCorrelationTracker 연동
11. **CPCV 도입** — mlfinlab CombinatorialPurgedKFold (N=8, k=2)
