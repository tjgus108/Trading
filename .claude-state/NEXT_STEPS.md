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
- Cycle 81 (Category C): DataFeed 캐시 TTL 경계
  - tests/test_feed_boundary.py 추가: TestCacheTTLBoundaries 클래스
  - test_cache_ttl_zero_disables_cache: ttl=0 경우 모든 요청 미스 확인 (connector.fetch_ohlcv.call_count=2)
  - test_cache_ttl_very_large_value: ttl=999999999 경우 캐시 항상 유효 확인 (call_count=1)
  - 전체 4 테스트 통과 (test_feed_boundary.py)
- Cycle 81 (Category A): BacktestReport JSON 로드/저장 round-trip
  - src/backtest/report.py: from_json() 클래스메서드 추가 (to_json()과 대칭)
  - inf/nan 값 문자열 변환 및 역변환 처리 (JSON 직렬화 호환성)
  - tests/test_backtest.py: 3개 테스트 추가
    - test_backtest_report_json_round_trip: 전체 필드 검증
    - test_backtest_report_json_special_values: inf/nan 복원 확인
    - test_from_json_preserves_dict_equality: dict 동등성 검증
  - 전체 12 테스트 통과 (test_backtest.py), 29 테스트 통과 (test_backtest_engine.py)
- Cycle 82 (Research): 과적합 백테스트 전략 실전 수정 베스트 프랙티스
  - Walk-Forward Optimization: WFE > 70% 기준, 파라미터 미변경으로 OOS 구간 테스트
  - 파라미터 안정성: optima 주변 sweep으로 plateau(안정) vs cliff(과적합) 구분
  - DSR(Deflated Sharpe Ratio) 사용 — 전략 수 및 선택 편향 보정
  - 의심 신호: Sharpe > 3.0, PF >> 2.0, 수수료/슬리피지 추가 시 수익 소멸
- Cycle 82 (Category SIM): Paper Simulation & Auto-improve
  - Paper Simulation 결과: 15 수익 전략, 7 손실 전략
  - Top 3: order_flow_imbalance_v2 (+16.45%), linear_channel_rev (+15.76%), momentum_quality (+14.38%)
  - Bottom 3: wick_reversal (-14.17%), engulfing_zone (-12.74%), frama (-7.89%)
  - wick_reversal 개선 적용:
    * 추세 필터 추가 (14기간 high/low 대비)
    * 신호 임계값 강화 (wick_ratio > 0.6→0.65)
    * 거래 빈도 제어 (80개→20개 거래, 75% 감소)
    * 개선 후 합성 데이터 테스트: 4.07% 수익, 20 거래, SR 1.62, MDD 4.6%
  - 모든 wick_reversal 관련 테스트 16개 통과

## 남은 작업
- TWAP per-slice 타임아웃(dry_run=False 경로) 추가 커버리지 고려
- 거래소 커넥터 통합 테스트 (mock connector 기반)
