# Next Steps

## 완료
- Cycle 75: TWAP 타임아웃 경계 테스트 2개 추가
- Cycle 76: LSTM numpy fallback 회귀 테스트 추가
  - test_train_torch_save_path_is_valid: model_path 유효성 검증
  - test_train_torch_saved_data_contains_n_features: n_features=seq_X_raw.shape[-1] 검증

## 남은 작업
- TWAP per-slice 타임아웃(dry_run=False 경로) 추가 커버리지 고려
- 거래소 커넥터 통합 테스트 (mock connector 기반)
