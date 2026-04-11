# Cycle 21 - 진행 상황

## 완료: DEX Feed 강화 (재시도 + fallback)

### 이번 작업 내용 (Cycle 21)
`src/data/dex_feed.py` — 재시도 로직 + CoinGecko fallback 추가

**주요 변경:**
1. **exponential backoff 재시도** (line 107-149)
   - `_fetch_coingecko_with_retry()` 메서드 추가
   - 재시도 간격: 1s, 2s (Cycle 6 패턴)
   - max_retries=2 (기본값)

2. **Fallback 메커니즘** (line 43-56)
   - `_last_successful[symbol]` 저장소
   - API 실패 → fallback → 0.0 단계 처리
   - get_price()에서 명시적 처리

3. **하위호환 유지**
   - `_fetch_coingecko()` 원본 메서드 보존
   - __init__ max_retries 파라미터 추가

### 변경 파일
- `src/data/dex_feed.py` — lines 26-27, 43, 44-56, 107-149
- `tests/test_dex_feed.py` (신규) — 15개 테스트

### 테스트 결과
```
15 passed in 0.72s (test_dex_feed.py)
```

테스트 커버리지:
- BasicTests: 7개 (mock, get_price, get_spread)
- RetryTests: 4개 (재시도 성공, fallback, 타이밍)
- CacheTests: 2개 (TTL 유효/만료)
- SymbolTests: 2개 (BTC/ETH 변형)

## 다음 단계
- OrderFlow VPIN 성능 최적화 (옵션)
- Telegram notifier 포맷 개선 (Cycle 20 미완)
