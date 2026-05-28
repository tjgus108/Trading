# Next Steps

_Last updated: 2026-05-28 (Cycle 235 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 228 → 235 (8사이클)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 228 | E+A+SIM+F | PaperTrader load_state 검증, TWAP unfilled_qty, regime 통합테스트 |
| 229 | C+B+SIM+F | order_book_depth, 동적 타임아웃, --mc-p-threshold 옵션 |
| 230 | D+E+SIM+F | depth_imbalance 피처, TWAP 동적 슬라이스, SPA 분석 |
| 231 | A+C+SIM+F | 테스트 32개 추가, OFICalculator, MC block_size, Fractional Kelly |
| 232 | B+D+SIM+F | KellySizer dynamic fraction, VPIN 피처, Sharpe IC, 버그 1건 수정 |
| 233 | C+B+SIM+F | OFI/VPIN 상관성 분석, Kelly+MDD 통합, --pass-ratio 인자 추가 |
| 234 | D+E+SIM+F | bid_ask_depth_imbalance 제거, regime fold weighting, TWAP volume-weights |
| 235 | A+C+SIM+F | **MC test 버그 수정** (0→7/11/4 PASS), block_size 36→72 |

### 🎯 Cycle 236 작업 방향 (236 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): PASS 전략 리스크 파라미터 최적화
- Cycle 235 Paper SIM PASS 전략 확인:
  - BTC PASS 7종: price_action_momentum, momentum_quality, cmf, volume_breakout, order_flow_imbalance_v2, htf_ema, positional_scaling
  - ETH PASS 11종: supertrend_multi(4/4!), cmf, price_action_momentum, volatility_cluster, volume_breakout, order_flow_imbalance_v2, momentum_quality, roc_ma_cross, narrow_range, htf_ema, value_area
  - SOL PASS 4종: cmf, momentum_quality, order_flow_imbalance_v2, volatility_cluster
- **크로스-심볼 안정 전략** (2심볼 이상 PASS): cmf, momentum_quality, order_flow_imbalance_v2
- `src/risk/kelly_sizer.py`: cmf/momentum_quality/ofi_v2에 특화된 Kelly 파라미터 검토
  - 현재: dynamic_fraction=0.5 (Cycle 232 추가)
  - 제안: PASS 전략은 fraction 0.6까지 허용, FAIL은 0.3으로 축소
- `src/risk/drawdown_monitor.py`: supertrend_multi 4/4 PASS → MDD 10.6% 우수, max_drawdown_limit 20%→18% 검토

#### D(ML): PASS 전략 피처 중요도 분석
- order_flow_imbalance_v2: 3심볼 PASS, OFI + VPIN 피처 기여도 확인
  - `src/ml/features.py`: VPIN/OFI 피처가 RandomForest에서 어느 정도 weight?
  - 피처 중요도 상위 5개 추출 → 다음 피처 엔지니어링 방향
- `src/ml/trainer.py`: walk_forward training에 supertrend_multi 시그널 통합 가능성 검토
  - ETH supertrend_multi: Sharpe 5.54, 4/4 PASS → IS 신호 안정성 높음

#### F(리서치): 크로스-심볼 전략 일관성 + 4h OOS 개선 방향
- cmf + momentum_quality + order_flow_imbalance_v2: 왜 3심볼 PASS인가?
  - 공통점: 트렌드 추종 + OFI 기반 진입 조건
  - BTC/ETH/SOL 모두 변동성 구조가 비슷한 블록 부트스트랩에서 강함
- run_bundle_oos.py 4h OOS: IS Sharpe 전부 음수 문제
  - 4h GBM block_size도 72로 업데이트 필요 (현재 기본값 36)
  - `scripts/run_bundle_oos.py` 내 block_size 설정 확인

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만 — 실전 데이터 PASS 기준 미충족

### 핵심 메트릭 (Cycle 235 기준)
- **크로스-심볼 PASS (2종+)**: cmf, momentum_quality, order_flow_imbalance_v2, volume_breakout, htf_ema
- **최강 단일 심볼**: ETH supertrend_multi (4/4, Sharpe 5.54), BTC price_action_momentum (3/4, Sharpe 5.21)
- **테스트**: 8,127 passed (Cycle 235 변화 없음 — 코드 수정만)
- **핵심 인프라 수정**:
  - MC test 버그 수정: equity-curve Sharpe vs trade PnL 단위 불일치 → 동일 기준 비교로 통일
  - BlockBootstrap block_size 36→72 (3일 블록, 추세 보존 강화)
