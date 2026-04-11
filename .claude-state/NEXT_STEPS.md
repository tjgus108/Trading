# Next Steps

## 완료
- Cycle 75: TWAP 타임아웃 경계 테스트 2개 추가
- Cycle 77: Heston 경계 조건 4개 테스트 통과 (소량 데이터, 고/저변동성, 데이터 부족)
- Cycle 76: LSTM numpy fallback 회귀 테스트 추가
  - test_train_torch_save_path_is_valid: model_path 유효성 검증
  - test_train_torch_saved_data_contains_n_features: n_features=seq_X_raw.shape[-1] 검증
- Cycle 77 (Research): Stoch Vol 모델 실전 적용 조사
  - Heston 단독보다 Heston+LSTM 하이브리드가 실전 성과 우위 (Sharpe 2.1, BTC 2024)
  - GARCH vs SV 순수 예측력 차이는 미미, 고변동성 구간에서 둘 다 정확도 하락
  - 실용적 결론: 봇에는 GARCH(빠른 피팅) + ML 보정 조합이 현실적

## 남은 작업
- TWAP per-slice 타임아웃(dry_run=False 경로) 추가 커버리지 고려
- 거래소 커넥터 통합 테스트 (mock connector 기반)
