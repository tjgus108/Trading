# Next Steps

_Last updated: 2026-04-18 (Cycle 144 - 레짐 필터 구현 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 145
- 145 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** (표 기준 Cycle 5 패턴)

### ✅ Cycle 144 완료 사항

#### 작업 1: live_paper_trader 레짐 필터
- **상태**: ✅ COMPLETE
- `LiveState` 클래스에 `regime_states` 필드 추가
  - symbol별 현재 레짐 추적
  - RANGING에서 건너뛴 신호 카운트 기록
- `_tick_symbol()` 메서드 개선
  - 레짐 변화 감지 로깅 추가 ("[CHANGED]" 표시)
  - RANGING 필터링 시 skipped_count 증가
- `_generate_report()` 개선
  - 리포트에 심볼별 레짐 정보 출력
  - "Regime: RANGING | Skipped (RANGING): 12" 형식
- 상태 파일에 regime_states 저장 → 재시작 후에도 추적 가능

#### 작업 2: DataFeed 레짐 캐시 (선택사항)
- **상태**: ✅ COMPLETE (간단한 버전)
- `DataFeed` 클래스에 `_regime_cache` 추가
  - 간단한 TTL 캐시 (기본 5분)
- 새 메서드 추가:
  - `cache_regime(symbol, regime_value, ttl)` — regime 저장
  - `get_cached_regime(symbol)` — regime 조회 (만료 체크)
  - `clear_regime_cache(symbol=None)` — 캐시 삭제
- `invalidate_cache()` 개선
  - `regime_cache_too` 파라미터 추가

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **하지만 두 가지 유효한 경로 발견:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인**
- BTC 1000캔들(42일): test acc 63.5%, val 67.3% → **PASS**
- 1500+ 캔들에서는 FAIL (레짐 변화로 패턴 소멸)
- **구현 방향**: 최근 1000캔들로 학습, 주 1회 재학습, binary_threshold=0.01
- 코드: `scripts/train_ml.py --binary --bybit --limit 1000`

#### 경로 2: 레짐 필터링 ← **지금 여기 구현 완료**
- BTC 레짐 분석 결과:
  - RANGING (1213 candles, 28%): 모든 전략 -3~-4 Sharpe → **거래 금지** ✅
  - TREND_UP (350 candles, 8%): narrow_range Sharpe +1.25 → 조건부 활성화
  - TREND_DOWN (739 candles, 17%): 대부분 음수 → 거래 금지 or 숏 전용
- **구현 완료**: live_paper_trader에 레짐 필터 추가, RANGING에서 시그널 무시 ✅

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

**다음 구현 과제 (우선순위):**
1. **ML 자동 재학습 파이프라인** — 주 1회, 최근 1000캔들
2. **ML 시그널 live 연동** — PASS 모델 로드 → 시그널 생성
3. **Regime 기반 동적 포지션 사이징** — TREND_UP에서 +30%, TREND_DOWN에서 -50% 또는 숏만 활성화
4. 합성 데이터 GARCH 교체
5. 전략 상관관계 모니터링
