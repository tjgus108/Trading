# Cycle 120: Wick Reversal Research

## [2026-04-12] Cycle 120 — Wick Reversal
- Hammer/Shooting Star: 68% daily reversal accuracy (ChartSchool). 위꼬리/아래꼬리 비율 >60%, 다음 봉 확인+볼륨이 성공률 결정적 요소.
- 2025 실전: 고점 Shooting Star → 10% 하락 사례 확인. 확인 캔들 없이 진입 시 실패율 높음.
- `wick_reversal` 전략 이미 구현됨 (`src/strategy/wick_reversal.py`, registry 등록 완료). 개선 포인트: 다음 봉 확인 로직 추가 고려.

## 기존 구현 상태
- 파일: `src/strategy/wick_reversal.py` — WickReversalStrategy (wick_ratio > 0.65, SMA20 필터, 볼륨, 추세 필터)
- Registry: ✅ 등록됨 (`"wick_reversal": WickReversalStrategy`)
- 테스트: `tests/test_wick_reversal.py` 존재

## 개선 가능 포인트 (다음 Cycle)
1. 다음 봉 확인(confirmation candle) 로직 추가 → false signal 감소
2. 볼륨 임계값 상향 (현재 avg*0.8 → avg*1.2)
3. RSI 극단값 필터 추가 (Hammer RSI<40, ShootingStar RSI>60)

---
Updated: 2026-04-12 Cycle 120
