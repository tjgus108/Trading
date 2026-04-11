# Cycle 58 - Research: Bot Running Costs

## [2026-04-11] Cycle 58 — Bot Running Costs
- VPS: $20~40/월 (기본), $100~200/월 (고성능 멀티봇)
- API: 거래소 API 자체는 무료, 3rd-party 봇 플랫폼 구독료 별도 ($25~240+/월)
- 전력/유지보수: 클라우드 기준 별도 전력비 없음, 관리 기회비용 $150~600/월 (주 3시간 기준)
- 현실적 최소 비용: VPS $20 + 관리시간 → 월 $50~100 수준이면 자체 봇 운영 가능

---

# Cycle 56 - Data & Infrastructure 캐시 키 검증 완료

## [2026-04-11] Cycle 56 — DataFeed 멀티 심볼 캐시 키 충돌 검증

### 작업 완료
- `src/data/feed.py` 캐시 구조 검증
  - 캐시 키: (symbol, timeframe, limit) 튜플 (line 97)
  - 서로 다른 심볼/타임프레임 조합 시 고유 키 생성 확인

### 테스트 추가
- `tests/test_feed_parallel.py`:
  - `test_cache_key_no_collision_multi_symbol` (lines 147-192):
    - 4개 조합 (BTC/USDT 1h, ETH/USDT 1h, BTC/USDT 4h, ETH/USDT 4h) 동시 페치
    - 캐시 통계로 4개 미스 + 4개 고유 키 검증
    - 같은 조합 재페치 시 캐시 히트 확인
    - API 호출 횟수 검증 (4회 후 변화 없음)

### 테스트 결과
- tests/test_feed_parallel.py: 23/23 PASS ✓
  - 신규 test_cache_key_no_collision_multi_symbol PASS
  - 기존 22개 테스트 모두 통과 (회귀 없음)

---

# Cycle 55 - Config Migration Helper 완료

## [2026-04-11] Cycle 55 — migrate_config 헬퍼 추가

### 작업
- `src/config.py`: `migrate_config(raw)` 함수 추가 (line 187)
  - 구버전 키 `risk.stop_loss` → `risk.stop_loss_atr_multiplier` 자동 변환
  - 구버전 키 `risk.take_profit` → `risk.take_profit_atr_multiplier` 자동 변환
  - 누락 risk/trading 필드에 기본값 자동 채움 + UserWarning 발생
  - `load_config()`에서 yaml 파싱 직후 호출
  - `rsk.get("stop_loss", ...)` → `rsk.get("stop_loss_atr_multiplier", ...)` 수정

### 테스트 추가
- `tests/test_config.py`:
  - `test_migrate_config_renames_old_keys`: 구버전 키 변환 + 경고 확인
  - `test_migrate_config_fills_missing_defaults`: 누락 필드 기본값 채움 확인

### 테스트 결과
- tests/test_config.py: 10/10 PASS

---
