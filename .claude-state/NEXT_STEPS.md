# Next Steps

_Last updated: 2026-04-18 (Cycle 148 - F 리서치: DC+Meta-Learning, Regime-RL 논문, 봇 실패패턴)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 148
- 148 mod 5 = 3 → **E(실행) + A(품질) + F(리서치)** (표 기준 Cycle 3 패턴)

### ✅ Cycle 147 완료 사항

#### 작업 1: 레짐 기반 포지션 사이징 live 연동 ✅ COMPLETE
- live_paper_trader: REGIME_SIZE_MULT (TREND_UP 1.3x, TREND_DOWN 0.5x, HIGH_VOL 0.3x)
- DrawdownMonitor: set_regime() + HIGH_VOL에서 일일 DD 2%로 축소

#### 작업 2: ML PFI 분석 자동화 ✅ COMPLETE
- train_ml.py: auto-retrain 후 PFI 자동 실행, feature_importance JSON 저장
- RF: max_features='sqrt' 명시적 지정

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
2. **live_paper_trader 실제 운영** — `/usr/local/bin/python3.11 scripts/live_paper_trader.py --days 7 --ml-filter`
3. **ETH/SOL ML 모델 개선** — rsi14, rsi_zscore, price_vs_vwap 제거 후 재학습 (PFI 근거)
4. **전략 상관관계 모니터링** — 활성 전략 간 상관 측정, 과집중 경고
5. **CPCV 도입** — mlfinlab CombinatorialPurgedKFold (N=8, k=2)
