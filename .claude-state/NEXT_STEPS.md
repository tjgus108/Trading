# Next Steps

## 완료
- Cycle 75: TWAP 타임아웃 경계 테스트 2개 추가
  - test_twap_global_timeout_triggers_on_second_slice: elapsed > budget → 조기 종료
  - test_twap_global_timeout_not_triggered_within_budget: elapsed < budget → 정상 완료

## 남은 작업
- TWAP per-slice 타임아웃(dry_run=False 경로) 추가 커버리지 고려
- 거래소 커넥터 통합 테스트 (mock connector 기반)
