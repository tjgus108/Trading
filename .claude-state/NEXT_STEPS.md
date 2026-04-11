# Cycle 27 - Risk: Session Filter 통합 완료

## 이번 작업 내용
Cycle 25의 `is_active_session()` 헬퍼를 RiskManager에 통합.

**수정:**
1. `src/risk/manager.py`
   - L12–L15: `datetime`, `Union`, `SessionType`, `is_active_session` import 추가
   - L111, L119: `__init__`에 `session_filter: bool = False` 파라미터 + 저장
   - L178: `evaluate()`에 `timestamp: Union[datetime, None] = None` 파라미터 추가
   - L226–L240: 세션 필터 블록 — REDUCED+평일 → 50%, REDUCED+주말 → 30% 축소

2. `tests/test_risk_manager.py`
   - L255–L285: `test_session_filter_reduced_asia_halves_position` (평일 아시아)
   - L286–L300: `test_session_filter_weekend_scales_to_30_pct` (주말)

## 설계 결정
- 기본값 `session_filter=False` → 기존 코드 동작 변경 없음 (opt-in)
- 주말 판단: `timestamp.weekday() >= 5` (is_active_session 내부와 동일 로직)
- 포지션 축소는 jitter 적용 이후 — 순서: 기본 사이징 → 클램프 → jitter → 세션 축소

## 다음 단계
- `config/config.yaml`에 `session_filter: true/false` 연결 가능
- FORCE_LIQUIDATE 테스트 통합 강화 (옵션 2) 미완료
