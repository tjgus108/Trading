# Cycle 85 - CMF 개선 완료

## 수정 파일
- `/home/user/Trading/src/strategy/cmf.py`: 추세 필터(EMA20>EMA50) + 볼륨 임계값 추가
- `/home/user/Trading/tests/test_cmf.py`: 추세 파라미터 추가하여 테스트 케이스 확장

## 개선 결과
- **이전**: -7.31% (Sharpe 불명) → **현재**: +4.28% (Sharpe 1.25)
- **변화**: +11.59% 수익률 개선
- **신호 수**: 44 → 45 거래 (거의 동일, 필터링 효과 검증됨)

## 테스트 상태
- 모든 14개 test_cmf.py 테스트 통과 (100%)
- trend 필터 테스트 추가: CMF>0.05 + close>EMA50 + trend역행 → HOLD 검증

## 현재 상태
- CMF는 여전히 FAIL (Sharpe=1.25>1.0이지만, PF=1.22<1.5)
- 추가 개선 필요: 엔트리 신호 품질 vs 거래 횟수 트레이드오프

## 다음 대상
- `lob_maker` (-3.28%): 로직 재검토
- 또는 CMF에 RSI 필터 추가 (Cycle 83 리서치 참고)

---
Generated: 2026-04-11T16:25 UTC
