# Next Steps

_Last updated: 2026-05-29 (Cycle 239 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 238, 239

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 238 | E+A+SIM+F | rolling Sharpe 모니터, perturbation_check, block_size 24, regime death 리서치 |
| 239 | C+B+SIM+F | reconnect_gaps, cache_stats, MDD kill switch, vol_scaling, --perturbation-check CLI |

### 🎯 Cycle 240 작업 방향 (240 mod 5 = 0 → D(ML) + E(실행) + F(리서치))

#### D(ML): 레짐별 SHAP 피처 중요도 분리
- features.py 피처 중요도를 레짐 레이블별 분리 추적
  - TREND에서 모멘텀 피처 우세 vs HIGH_VOL에서 VPIN/OFI 우세 확인
- ACF 기반 자동 block_size 선택 검토
- ML 모델 health 모니터링 개선

#### E(실행): Orchestrator에 kill_switch 연동
- RiskManager/Orchestrator에서 should_kill_strategy() 호출 연동
- apply_volatility_scaling()을 KellySizer 메인 로직에 통합
- 오더북 깊이 기반 포지션 사이즈 제한 검토 (리서치 기반)

#### SIM: --block-size 비교 시뮬
- --block-size 12 / 24 / 36 비교 (합성 데이터)
- --perturbation-check 활성화하여 Top 전략 ROBUST/FRAGILE 판정

#### F(리서치): KS-test 분포 drift + equity curve std
- scipy.stats.ks_2samp 기반 수익률 분포 변화 감지
- equity curve rolling std 이상 감지 패턴
- 오더북 깊이 기반 동적 포지션 사이즈 산식 조사

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8,240+ passed (Cycle 239 +42개)
- 신규: MDD kill switch, vol_scaling, reconnect_gaps, cache_stats, --perturbation-check CLI
