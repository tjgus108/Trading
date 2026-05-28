# Next Steps

_Last updated: 2026-05-28 (Cycle 237 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 완료된 사이클: 233, 234, 235, 237 (이 세션)

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 233 | E+A+SIM+F | PaperTrader get_execution_summary, HealthChecker get_uptime_pct |
| 234 | D+E+SIM+F | bid_ask_depth_imbalance 제거, regime fold weighting, TWAP volume-weights |
| 235 | A+C+SIM+F | MC permutation 버그 수정(block sign), --block-size CLI, WebSocket MAX_BACKOFF |
| 237 | B+D+SIM+F | perturbation_check() BacktestEngine, get_all_regime_importances() RegimeAwareFeatureBuilder |

### 🎯 Cycle 238 작업 방향 (238 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): OOS Sharpe std 임계값 재검토
- `scripts/run_bundle_oos.py`: OOS Sharpe std 임계값 1.5 → 실거래소/합성 데이터 분리 적용
  - 합성 데이터(GBM): std_threshold=3.0 (완화)
  - 실거래소 데이터: std_threshold=1.5 (유지)
  - `--data-source synthetic|real` CLI arg 추가
- WebSocket feed 안정성: MAX_BACKOFF=60s + jitter 추가 검토
- DataFeed 캐시 전략: TTL 기반 만료 + 강제 갱신 옵션

#### B(리스크): perturbation_check() 실전 통합
- `BacktestEngine.run()` 결과에 perturbation_check 선택적 실행 옵션 추가
  - `run(..., run_perturbation=False)` 파라미터 (기본 Off, 속도 유지)
  - WalkForwardEngine 통합: fold 완료 후 best params로 섭동 체크
- DrawdownMonitor + KellySizer dual dampening (HIGH_VOL):
  - HIGH_VOL 레짐에서 DrawdownMonitor.get_mdd_size_multiplier() × KellySizer._REGIME_SCALE["HIGH_VOL"] 동시 적용
  - 현재는 독립적 — 통합 메서드 `get_combined_multiplier(regime)` 추가 검토

#### F(리서치): 합성 데이터 한계 극복 방안
- Cycle 235 이후 지속된 0 PASS 원인: GBM 합성 데이터 fat-tail/autocorrelation 미재현
- GAN 기반 합성 데이터(TimeGAN, FinGAN) 생성 검토:
  - src/data/synthetic_generator.py 신규 모듈 (GBM 대체)
  - 구현 부하 크므로 리서치만 수행
- 롤링 Sharpe 모니터링 실전 적용 케이스 조사

### 시뮬레이션 분석 결과

#### Paper Simulation 상위 전략 (BTC/USDT, 합성 데이터)
| 순위 | 전략 | Sharpe | Sharpe Std | PF | Trades |
|------|------|--------|-----------|-----|--------|
| 1 | momentum_quality | 6.01 | 0.75 | 1.83 | 126 |
| 2 | volume_breakout | 4.34 | 0.40 | 1.67 | 96 |
| 3 | price_action_momentum | 4.20 | 1.69 | 1.48 | 157 |
| 4 | supertrend_multi | 4.15 | 1.98 | 1.64 | 100 |

**Sharpe std 최소 전략** (파라미터 안정성 우수): volume_breakout(0.40), momentum_quality(0.75)

#### Bundle OOS (BTC/USDT 4h, 합성 데이터) — 2026-05-28T20:17
- 0/5 PASS — narrow_range 3/9 fold pass (최다)
- 모든 OOS Sharpe std > 1.5 → GBM 데이터 한계
- 실거래소 데이터 연결 시 재평가 필요

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만
- MC permutation test는 합성 GBM 데이터에서 p_value 항상 > 0.05 (alpha 부재)

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 6.01), volume_breakout(Sharpe 4.34), price_action_momentum(Sharpe 4.20)
- 테스트: 8,211 passed (Cycle 237 +31개)
- 신규 기능: perturbation_check() (FRAGILE/ROBUST 판정), get_all_regime_importances() (레짐별 RF 중요도)
