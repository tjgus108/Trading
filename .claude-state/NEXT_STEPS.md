# Next Steps

_Last updated: 2026-05-29 (Cycle 238 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 238

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 238 | E+A+SIM+F | rolling Sharpe 모니터, perturbation_check, block_size 24, regime death 리서치 |

### 🎯 Cycle 239 작업 방향 (239 mod 5 = 4 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): DataFeed 캐시 최적화 + OFI 정확도
- DataFeed 캐시 hit rate 로깅 추가 검토
- OFICalculator 극단값 감지 로직 검증
- WebSocket reconnect 후 데이터 갭 처리 개선

#### B(리스크): MDD Circuit Breaker 강화 (리서치 기반)
- 리서치 결과 적용: 백테스트 MDD의 1.5x 초과 시 전략 자동 disable
- DrawdownMonitor에 `mdd_kill_switch(backtest_mdd, multiplier=1.5)` 추가
- KellySizer + DrawdownMonitor 이중 감쇠가 HIGH_VOL에서 올바르게 작동하는지 검증
- Kelly-VIX Hybrid: `fraction × (target_vol / realized_vol_20d)` volatility scaling

#### SIM: perturbation_check 활용 시뮬레이션
- Top 3 전략에 perturbation_check 적용 → ROBUST/FRAGILE 판정
- --block-size 12 / 36 비교 시뮬 (24와 대조)
- momentum_quality, price_action_momentum PASS 가능성 재평가

#### F(리서치): KS-test 분포 drift + equity curve std
- scipy.stats.ks_2samp 기반 수익률 분포 변화 감지
- equity curve rolling std 이상 감지 패턴
- GAN 기반 합성 데이터 생성 가능성 (GBM 대체)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8,200+ passed (Cycle 238 +27개)
- 신규: perturbation_check(ROBUST/FRAGILE), rolling Sharpe 30d, block_size 24
