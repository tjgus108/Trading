# Next Steps

_Last updated: 2026-04-18 (Cycle 145 - ML 시그널 live 연동 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 146
- 146 mod 5 = 1 → **A(품질) + C(데이터) + F(리서치)** (표 기준 Cycle 1 패턴)

### ✅ Cycle 145 완료 사항

#### 작업 1: live_paper_trader에 ML 시그널 연동 준비 ✅ COMPLETE
- **상태**: ✅ COMPLETE (Execution Agent 준비 완료)
- 3개 ML 유틸 함수 추가:
  - `load_ml_model(symbol)` — models/{symbol}_*_rf_binary.pkl 자동 로드
  - `get_ml_features(df)` — 필수 피처(rsi14, atr14, sma20, ema50, bb_upper, bb_lower, volume_sma20, return_5, macd, vwap) 생성
  - `predict_ml_signal(model, features, scaler)` — UP/DOWN 이진 분류 예측 (confidence 포함)
- `LivePaperTrader` 클래스 수정:
  - `ml_filter_enabled` 플래그 추가 (command line: `--ml-filter`)
  - `ml_models` dict로 심볼별 (model, scaler) 저장
  - `initialize()` 메서드: --ml-filter 활성화 시 모델 자동 로드
  - `_tick_symbol()` 시그널 생성 후 ML 필터 적용:
    - BUY 시그널 + ML DOWN → 차단 (상승 신호 없음)
    - SELL 시그널 + ML UP → 차단 (하락 신호 없음)
    - 필터된 신호는 로그에 기록 (confidence 포함)
- docstring 업데이트 (옵션 설명 추가)
- 모든 TWAP 테스트 통과 (38개)

#### 작업 2: TWAP 실행기 상태 검증 ✅ COMPLETE
- **상태**: ✅ COMPLETE
- TWAP 기본 동작 정상 확인:
  - dry_run 모드: 슬리피지 시뮬레이션 ±0.05%
  - 부분 체결 추적 (fill_ratio 기반)
  - 글로벌 타임아웃: `timeout_per_slice * n_slices`
- 코드 개선:
  - 라인 180: `result.get("filled", slice_qty)` → `result.get("filled", 0.0)` (더 안전한 기본값)
  - 실패 슬라이스 처리: filled_qty = 0 명시적 기록
- 모든 TWAP 테스트 통과

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**
- 1500+ 캔들: FAIL (레짐 변화로 패턴 소멸)
- 구현 방향: 최근 1000캔들 + 주 1회 재학습 + binary_threshold=0.01
- 라이브 연동: `--ml-filter` 옵션으로 활성화 (위의 작업 1)

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

**다음 구현 과제 (우선순위):**
1. **ML 모델 실제 생성** — BTC/ETH/SOL에서 1000캔들 WF로 PASS 모델 학습 & 저장
2. **Regime 기반 동적 포지션 사이징** — TREND_UP에서 +30%, TREND_DOWN에서 -50% 또는 숏만 활성화
3. **live_paper_trader 검증 실행** — 7일 운영 (--days 7 --ml-filter 옵션)
4. 합성 데이터 GARCH 교체
5. 전략 상관관계 모니터링
