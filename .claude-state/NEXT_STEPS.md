# Cycle 88 - Q1 2026 리서치

## [2026-04-11] Cycle 88 — Q1 2026 Lessons
- BTC Q1 -22%, 고점 대비 -30% 하락 — 트렌드 추종 봇은 whipsaw로 손실
- 그리드/DCA 전략이 횡보 구간(전체 60~70%)에서 상대적으로 유리
- 과최적화(curve-fitting) 봇은 레짐 전환 시 실패 — 백테스트 성과 ≠ 실거래
- circuit breaker 미탑재 봇은 플래시크래시 시 최악 가격에 청산

## 시사점 (봇 개선 방향)
- 레짐 감지 강화 (trending vs. ranging 구분)
- MDD 방어용 circuit breaker 로직 추가 고려
- lob_maker PF 1.5 미달 — VPIN 임계값 상향 재시도

## 이전 미완성
- lob_maker Profit Factor 1.36 < 1.5 (FAIL)
- engulfing_zone 전략 개선 대기

---
# Cycle 87 - Regime Adaptive 전략 검증 완료

## 결과
- `test_regime_switch_low_confidence` PASS: 레짐 전환 시 confidence=LOW 정상 동작
- `test_generate_bull_regime` PASS: bull 레짐에서 SELL 신호 차단 정상 동작

### 검증 파일
- `/home/user/Trading/src/strategy/regime_adaptive.py` (수정 없음)
- `/home/user/Trading/tests/test_regime_adaptive.py`

## 다음 사이클
- lob_maker Profit Factor 1.5 이상 개선 고려
- engulfing_zone 전략 개선
