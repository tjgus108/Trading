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
- Cycle 78 (Research): Backtest vs Live 성과 갭 조사
  - Sharpe 40% 이상 하락 or MDD 2배 이상 → 과적합 신호
  - 주요 원인: 슬리피지(얇은 호가창), 레짐 변화, 전략 경쟁 심화
  - 실용: 3단계 파이프라인 (백테스트 → walk-forward → 라이브 페이퍼)
- Cycle 79 (Category C): Notifier HTML escape 추가
  - src/notifier.py: html.escape() 적용 (symbol, error, notes, timestamp 등)
  - TestHTMLEscape 클래스 추가: XSS 공격 방어 검증 (2 테스트)
  - 전체 25 테스트 통과
- Cycle 80 (Milestone): Dashboard Cycle 80 배지 추가 (#ff4500, 오렌지-레드)
  - src/dashboard.py: _milestones 리스트 맨 앞에 (80, "#ff4500", "#fff", "CYCLE 80 MILESTONE") 추가
  - tests/test_dashboard.py: test_render_html_cycle80_milestone, test_render_html_no_cycle80_below_80 추가 (16 테스트 통과)
- Cycle 80 (Category D): AdaptiveSelector rolling Sharpe 가중치 변동성 검증
  - test_weight_shifts_with_changing_sharpe: PnL 패턴 변화 시 Sharpe 갱신 확인
  - test_select_weight_proportional_after_reversal: Sharpe 역전 후 선택 빈도 변화 확인
  - 전체 20 테스트 통과 (EWM 없음, 단순 rolling window 방식 확인)
- Cycle 80 (Research): 입문자용 크립토 트레이딩 봇 자료 조사
  - 책: C.W. Morton "Ultimate Beginner's Guide to Crypto Trading Bots", Ernie Chan "Quantitative Trading"
  - 플랫폼: 3Commas(DCA/그리드봇), Cryptohopper(전략 마켓플레이스)
  - 실용: 단순 DCA/그리드 봇부터 시작 → walk-forward 검증 후 고급 전략으로

## 남은 작업
- TWAP per-slice 타임아웃(dry_run=False 경로) 추가 커버리지 고려
- 거래소 커넥터 통합 테스트 (mock connector 기반)
