# Next Steps

_Last updated: 2026-04-16 (Cycle 135 — Execution 개선 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 사이클 (Cycle 136) 힌트

### 로테이션 기준 다음 카테고리
- 136 mod 5 = 1 → **B(리스크) + C(데이터)**

### 우선 작업
1. **[A] 품질**: 테스트 33개 실패 수정 (이전 사이클 미완)
2. **[B] Risk**: Regime Detection 구현
3. **[C] 데이터**: 데이터 피드 장애 복구 로직 검증

### Cycle 135 완료 사항 (Execution)
- **[E] Telegram 알림**: `_send` 재시도(max 3) + exponential backoff, 4xx 즉시 포기/5xx+네트워크오류 재시도
- **[E] 주문 재시도**: `create_order` backoff 고정 1초 → exponential(1s,2s,4s..) 변경
- **[E] 데이터 조회 재시도**: `fetch_ohlcv`, `fetch_ticker`에 `_retry` 래퍼 추가 (NetworkError/RequestTimeout 자동 재시도)
- 테스트 9개 추가 (notifier retry 5 + connector retry/backoff 4)

### Cycle 135 완료 사항 (ML & Signals — 병렬 세션)
- paper_simulation: JSON/CSV 구조화 데이터 저장 추가 (PAPER_SIMULATION_RESULTS.json/.csv)
- paper_trader: 주문 크기 비례 슬리피지 (√(notional/$10k) 시장 충격 모델) 추가
- **[D] ML**: RF 피처 중요도를 모델 pkl에 저장 + 로드 시 top3 로깅 + `get_feature_importances()` API
- **[D] ML**: `compute_ensemble_weight_recency()` 추가 — 시간 감쇠(decay) 기반 최신 모델 우선 가중치
- **[D] ML**: `get_feature_importances()` sklearn 호환성 버그 수정 (CalibratedClassifierCV attribute error)

### Cycle 134 완료 사항
- paper_simulation: 전략 로드 실패/평가 오류 카운트 추적 및 경고 출력
- paper_simulation: run_simulation() 전체 심볼 실패 시 exit code 1 반환
- paper_connector: create_order(price=None) 시 $1.0 기본값 제거 → ValueError로 변경
- VPIN: zero-volume 윈도우 replace(0,1) 버그 수정 → NaN 처리 (잘못된 VPIN 값 방지)
- DataFeed: max_cache_size(128) LRU 퇴거 추가 → 무제한 메모리 증가 방지
- **[B] Risk**: KellySizer input validation (NaN/inf/범위외 win_rate 방어) + from_trade_history 소표본 Bayesian shrinkage
- **[B] Risk**: VaR/CVaR 소표본(T<30) parametric 크로스체크 보정 추가

### 이전 사이클 후속 과제
- Regime Detection 구현 필요 (리서치에서 업계 표준 확인)
- engulfing_zone/relative_volume 2개 전략 심화 개선 대기
- TWAP 비대칭 슬리피지 모델 실전 데이터 검증 필요
- paper_connector balance 수정 후 실제 paper trading 검증 필요
