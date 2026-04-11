# Cycle 60 - Research: 2026 Bot Must-Haves

## [2026-04-11] Cycle 60 — 2026 Bot Must-Haves
- AI 기반 멀티전략 동시 실행 (단일 전략 단독 운영 비권장)
- 멀티익스체인지 스마트 오더라우팅 (최적 유동성/가격 자동 선택)
- 동적 리스크 관리: 다단계 TP/SL, TWAP/VWAP 실행
- 규제 대응: AML/KYC 로그, 세금 리포트 자동화
- 실시간 백테스트 + 포워드테스트 파이프라인

---

# Cycle 60 - Signal confidence validation 완료

## [2026-04-11] Cycle 60 — Confidence enum 비정상 값 검증

### 작업 완료
- `tests/test_confidence_validation.py` (신규):
  - `test_invalid_string_raises`: "VERY_HIGH" → ValueError
  - `test_invalid_numeric_raises`: 0.9 → ValueError
  - `test_valid_confidence_values`: HIGH/MEDIUM/LOW 정상 확인
  - `test_signal_default_confidence_is_enum`: Signal 필드 타입 보존 확인

### 테스트 결과
- tests/test_confidence_validation.py: 4/4 PASS

---

# Cycle 59 - DataFeed _fetch_fresh 경계 처리 완료

## [2026-04-11] Cycle 59 — _fetch_fresh 빈 DataFrame 처리

### 작업 완료
- `src/data/feed.py` _fetch_fresh (line 239):
  - 빈 DataFrame 경계 처리 추가 (line 244-245)
  - `if df.empty: raise ValueError(...)` → IndexError 방지
  - raw 데이터 비어있을 시 명확한 에러 메시지

### 테스트 추가
- `tests/test_feed_boundary.py` (신규 파일):
  - `test_fetch_fresh_empty_dataframe`: 빈 데이터 → ValueError 검증
  - `test_fetch_fresh_single_candle_with_nan`: NaN 포함 데이터 → 정상 처리 확인

### 테스트 결과
- tests/test_feed_boundary.py: 2/2 PASS ✓
- tests/test_feed_parallel.py: 21/21 PASS ✓ (회귀 없음)

---

# Cycle 58 - Research: Bot Running Costs

## [2026-04-11] Cycle 58 — Bot Running Costs
- VPS: $20~40/월 (기본), $100~200/월 (고성능 멀티봇)
- API: 거래소 API 자체는 무료, 3rd-party 봇 플랫폼 구독료 별도 ($25~240+/월)
- 전력/유지보수: 클라우드 기준 별도 전력비 없음, 관리 기회비용 $150~600/월 (주 3시간 기준)
- 현실적 최소 비용: VPS $20 + 관리시간 → 월 $50~100 수준이면 자체 봇 운영 가능
